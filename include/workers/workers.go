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
	// communication channels
	reductorTerminationChannels := make(map[int]chan int, numberOfReductors)
	reductorChannels := make(map[int]chan models.Packet, numberOfReductors)
	writerChannels := make(map[int]chan models.Packet, numberOfReaders)

	// create a waitgroup for reader and writer go-routines (readers + writers)
	var wg sync.WaitGroup
	wg.Add(2 * numberOfReaders)

	// create a waitgroup for reductors
	var middleWg sync.WaitGroup
	middleWg.Add(numberOfReductors)

	// start the writers
	for i := range numberOfReaders {
		channel := make(chan models.Packet)
		writerChannels[i] = channel

		go func(id int, inputChannel chan models.Packet) {
			defer wg.Done()

			w := writer{
				path:         fmt.Sprintf("%s/%d.out", file.OutputDir, id),
				inputChannel: inputChannel,
			}
			w.start()

			close(inputChannel)
		}(i, channel)
	}

	logrus.WithField("writers", numberOfReaders).Info("writers start")

	// start the reductors
	for i := range numberOfReductors {
		channel := make(chan models.Packet)
		tchannel := make(chan int)

		reductorChannels[i] = channel
		reductorTerminationChannels[i] = tchannel

		go func(inputChannel chan models.Packet, termChannel chan int) {
			defer middleWg.Done()

			rd := reductor{
				memory:             make(map[string]*models.Packet),
				inputChannel:       inputChannel,
				writerChannels:     writerChannels,
				terminationChannel: termChannel,
			}
			rd.start()

			close(inputChannel)
		}(channel, tchannel)
	}

	logrus.WithField("reductors", numberOfReductors).Info("reductors start")

	// start the writers
	for i := range numberOfReaders {
		go func(id int) {
			defer wg.Done()

			r := reader{
				id:                id,
				offset:            int64(id) * int64(file.ChunkSize),
				chunkSize:         int64(file.ChunkSize),
				fileSize:          file.FileSize,
				filePath:          file.Path,
				reductorChannels:  reductorChannels,
				numberOfReductors: numberOfReductors,
			}
			r.start()
		}(i)
	}

	logrus.WithField("readers", numberOfReaders).Info("readers start")

	// wait for readers and writers
	wg.Wait()

	// send terminate signal to all reductors
	for _, channel := range reductorTerminationChannels {
		channel <- 1
	}

	// wait for reductors
	middleWg.Wait()

	logrus.Info("workers finished")
}
