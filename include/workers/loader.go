package workers

import (
	"fmt"
	"os"
	"sync"

	"github.com/sirupsen/logrus"
)

// loader starts the reader workers based on the log files
// and log file sizes.
type loader struct {
	// maximum number of readers
	numberOfReaders int

	// data directory path
	dataPath string

	// reductor channels
	reductorChannels map[int]chan string
}

// begin the loader worker.
func (l loader) begin() error {
	path := fmt.Sprintf("%s/trace_io_0.log", l.dataPath)

	// open the log file
	file, err := os.Open(path)
	if err != nil {
		return fmt.Errorf("failed to open the tracing file: %v", err)
	}
	defer file.Close()

	// get the file stat
	info, err := file.Stat()
	if err != nil {
		return fmt.Errorf("failed to get file stat: %v", err)
	}

	// get the file size and number of chunks
	size := info.Size()
	chunkSize := int(size / int64(l.numberOfReaders))

	logrus.WithFields(logrus.Fields{
		"path":       path,
		"size":       size,
		"chunk_size": chunkSize,
		"readers":    l.numberOfReaders,
	})

	// create a wait group for each reader
	var wg sync.WaitGroup
	wg.Add(l.numberOfReaders)

	// create and start readers
	for index := 0; index < l.numberOfReaders; index++ {
		// each reader will read a partition of a file
		go func(id int) {
			r := reader{
				id:               id,
				offset:           int64(id) * int64(chunkSize),
				chunkSize:        int64(chunkSize),
				fileSize:         size,
				filePath:         path,
				reductorChannels: l.reductorChannels,
			}

			defer wg.Done()
			r.start()
		}(index)
	}

	wg.Wait()

	return nil
}
