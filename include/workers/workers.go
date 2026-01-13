package workers

import (
	"fmt"
	"sync"

	"github.com/amirhnajafiz/flak-dashboard/pkg/models"

	"github.com/sirupsen/logrus"
)

// Run the workers (writers first, reductors, and finally readers).
func Run(
	numberOfReaders int,
	numberOfReductors int,
	file *models.File,
) {
	// communication channels: writers
	writerChannels := make(map[int]chan *models.Packet, numberOfReaders)
	writerTerminationChannels := make(map[int]chan int, numberOfReaders)

	// communication channels: reductors
	reductorChannels := make(map[int]chan *models.Packet, numberOfReductors)
	reductorTerminationChannels := make(map[int]chan int, numberOfReductors)

	// waitgroups
	var (
		readersWg                sync.WaitGroup
		reductorsWg              sync.WaitGroup
		writersWg                sync.WaitGroup
		readerReductorInFlightWg sync.WaitGroup
		reductorWriterInFlightWg sync.WaitGroup
	)

	// validation parameters
	var (
		readersReadLogs   = 0
		readersSentLogs   = 0
		reductorsReadLogs = 0
		reductorsSentLogs = 0
		writerSentLogs    = 0
		statLock          sync.Mutex
	)

	// start the writers
	for i := range numberOfReaders {
		writersWg.Add(1)

		writerChannels[i] = make(chan *models.Packet)
		writerTerminationChannels[i] = make(chan int)

		go func(id int) {
			defer close(writerChannels[id])
			defer writersWg.Done()

			path := fmt.Sprintf("%s/%d.out", file.OutputDir, id)

			w := writer{
				sentLogs:                 0,
				path:                     path,
				inputChannel:             writerChannels[id],
				termincationChannel:      writerTerminationChannels[id],
				reductorWriterInFlightWg: &reductorWriterInFlightWg,
			}

			if err := w.start(); err != nil {
				logrus.WithFields(logrus.Fields{
					"path":  path,
					"id":    id,
					"error": err,
				}).Panic("writer failed")
			}

			// update stats
			statLock.Lock()
			writerSentLogs += w.sentLogs
			statLock.Unlock()
		}(i)
	}

	logrus.WithFields(logrus.Fields{
		"count": numberOfReaders,
		"file":  file.Name,
	}).Info("writers start")

	// start the reductors
	for i := range numberOfReductors {
		reductorsWg.Add(1)

		reductorChannels[i] = make(chan *models.Packet)
		reductorTerminationChannels[i] = make(chan int)

		go func(id int) {
			defer close(reductorChannels[id])
			defer reductorsWg.Done()

			rd := reductor{
				readLogs:                 0,
				sentLogs:                 0,
				memory:                   make(map[string]*models.Packet),
				inputChannel:             reductorChannels[i],
				terminationChannel:       reductorTerminationChannels[i],
				writerChannels:           writerChannels,
				readerReductorInFlightWg: &readerReductorInFlightWg,
				reductorWriterInFlightWg: &reductorWriterInFlightWg,
			}
			rd.start()

			// update stats
			statLock.Lock()
			reductorsReadLogs += rd.readLogs
			reductorsSentLogs += rd.sentLogs
			statLock.Unlock()
		}(i)
	}

	logrus.WithFields(logrus.Fields{
		"count": numberOfReductors,
		"file":  file.Name,
	}).Info("reductors start")

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
				readLogs:                 0,
				sentLogs:                 0,
				reductorChannels:         reductorChannels,
				numberOfReductors:        numberOfReductors,
				readerReductorInFlightWg: &readerReductorInFlightWg,
			}
			if err := r.start(); err != nil {
				logrus.WithFields(logrus.Fields{
					"path":  file.Path,
					"id":    id,
					"error": err,
				}).Panic("writer failed")
			}

			// update stats
			statLock.Lock()
			readersReadLogs += r.readLogs
			readersSentLogs += r.sentLogs
			statLock.Unlock()
		}(i)
	}

	logrus.WithFields(logrus.Fields{
		"count": numberOfReaders,
		"file":  file.Name,
	}).Info("readers start")

	// wait for the readers
	readersWg.Wait()

	logrus.WithFields(logrus.Fields{
		"file": file.Name,
	}).Info("readers finished")

	// wait for the reader-reductor in flight events
	readerReductorInFlightWg.Wait()

	// send terminate signal to all reductors
	for _, channel := range reductorTerminationChannels {
		channel <- 1
	}
	reductorsWg.Wait()

	logrus.WithFields(logrus.Fields{
		"file": file.Name,
	}).Info("reductors finished")

	// wait for the reductor-writer in flight events
	reductorWriterInFlightWg.Wait()

	// send terminate signal to all writers
	for _, channel := range writerTerminationChannels {
		channel <- 1
	}
	writersWg.Wait()

	logrus.WithFields(logrus.Fields{
		"file": file.Name,
	}).Info("writers finished")

	// print validation information
	logrus.WithFields(logrus.Fields{
		"file":                file.Name,
		"readers read logs":   readersReadLogs,
		"readers sent logs":   readersSentLogs,
		"reductors read logs": reductorsReadLogs,
		"reductors sent logs": reductorsSentLogs,
		"writers wrote logs":  writerSentLogs,
	}).Info("logs stored")
}
