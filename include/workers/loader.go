package workers

import (
	"fmt"
	"os"
	"sync"
)

type loader struct {
	numberOfReaders int
	dataPath        string
}

func (l loader) begin() error {
	// open the log file
	file, err := os.Open(fmt.Sprintf("%s/trace_io_0.log", l.dataPath))
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

	fmt.Printf("file size is %d, and chunk size is %d\n", size, chunkSize)

	// create a wait group for each reader
	var wg sync.WaitGroup
	wg.Add(l.numberOfReaders)

	// create readers based on the number of chunks
	for index := 0; index < l.numberOfReaders; index++ {
		go func(id int) {
			r := reader{
				id:       id,
				path:     fmt.Sprintf("%s/trace_io_0.log", l.dataPath),
				offset:   int64(id) * int64(chunkSize),
				size:     int64(chunkSize),
				fileSize: size,
			}

			defer wg.Done()
			r.start()
		}(index)
	}

	wg.Wait()

	return nil
}
