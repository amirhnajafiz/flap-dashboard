package workers

import (
	"fmt"
	"sync"

	"github.com/amirhnajafiz/flak-dashboard/pkg/models"

	"github.com/sirupsen/logrus"
)

// Run the workers.
func Run(
	numberOfReaders int,
	numberOfReductors int,
	file *models.File,
) {
	// communication channels: writers
	writerChannels := make(map[int]chan models.Packet, numberOfReaders)
	writerTerminationChannels := make(map[int]chan int, numberOfReaders)

	// communication channels: reductors
	reductorChannels := make(map[int]chan models.Packet, numberOfReductors)
	reductorTerminationChannels := make(map[int]chan int, numberOfReductors)

	// create waitgroups
	var (
		readersWg                sync.WaitGroup
		reductorsWg              sync.WaitGroup
		writersWg                sync.WaitGroup
		readerReductorInFlightWg sync.WaitGroup
		reductorWriterInFlightWg sync.WaitGroup
	)

	// start the writers
	for i := range numberOfReaders {
		writersWg.Add(1)

		writerChannels[i] = make(chan models.Packet)
		writerTerminationChannels[i] = make(chan int)

		go func(id int) {
			defer close(writerChannels[id])
			defer writersWg.Done()

			w := writer{
				path:                     fmt.Sprintf("%s/%d.out", file.OutputDir, id),
				inputChannel:             writerChannels[id],
				termincationChannel:      writerTerminationChannels[id],
				reductorWriterInFlightWg: &reductorWriterInFlightWg,
			}
			w.start()
		}(i)
	}

	logrus.WithField("writers", numberOfReaders).Info("writers start")

	// start the reductors
	for i := range numberOfReductors {
		reductorsWg.Add(1)

		reductorChannels[i] = make(chan models.Packet)
		reductorTerminationChannels[i] = make(chan int)

		go func(id int) {
			defer close(reductorChannels[id])
			defer reductorsWg.Done()

			rd := reductor{
				memory:                   make(map[string]*models.Packet),
				inputChannel:             reductorChannels[i],
				terminationChannel:       reductorTerminationChannels[i],
				writerChannels:           writerChannels,
				readerReductorInFlightWg: &readerReductorInFlightWg,
				reductorWriterInFlightWg: &reductorWriterInFlightWg,
			}
			rd.start()
		}(i)
	}

	logrus.WithField("reductors", numberOfReductors).Info("reductors start")

	// start the readers
	for i := range numberOfReaders {
		readersWg.Add(1)

		go func(id int) {
			defer readersWg.Done()

			r := reader{
				id:                       id,
				offset:                   int64(id) * int64(file.ChunkSize),
				chunkSize:                int64(file.ChunkSize),
				fileSize:                 file.FileSize,
				filePath:                 file.Path,
				reductorChannels:         reductorChannels,
				numberOfReductors:        numberOfReductors,
				readerReductorInFlightWg: &readerReductorInFlightWg,
			}
			r.start()
		}(i)
	}

	logrus.WithField("readers", numberOfReaders).Info("readers start")

	// wait for the readers
	readersWg.Wait()

	// wait for the reader-reductor in flight events
	readerReductorInFlightWg.Wait()

	// send terminate signal to all reductors
	for _, channel := range reductorTerminationChannels {
		channel <- 1
	}
	reductorsWg.Wait()

	// wait for the reductor-writer in flight events
	reductorWriterInFlightWg.Wait()

	// send terminate signal to all writers
	for _, channel := range writerTerminationChannels {
		channel <- 1
	}
	writersWg.Wait()

	logrus.Info("workers finished")
}
