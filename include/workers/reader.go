package workers

import (
	"bufio"
	"fmt"
	"io"
	"os"
	"time"

	"github.com/sirupsen/logrus"
)

// reader worker gets its data from the loader and passes it to
// the reader-reductor distributer.
type reader struct {
	id       int
	path     string
	offset   int64
	size     int64
	fileSize int64
}

// start the reader worker.
func (r reader) start() {
	// open the log file
	fd, err := os.Open(r.path)
	if err != nil {
		logrus.Error(err)
	}
	defer fd.Close()

	time.Sleep(time.Duration(r.id+1) * time.Second)
	fmt.Printf("[reader %d] is reading from %d to %d\n", r.id, r.offset, r.offset+r.size)

	// seek to chunk start
	_, err = fd.Seek(r.offset, io.SeekStart)
	if err != nil {
		logrus.Error(err)
		return
	}

	reader := bufio.NewReaderSize(fd, 64*1024)

	chunkEnd := r.offset + r.size
	var currentPos int64 = r.offset

	// if not the first chunk, skip partial first line
	if r.offset > 0 {
		line, _ := reader.ReadString('\n')
		if len(line) > 0 {
			currentPos += int64(len(line))
		}
	}

	for {
		line, err := reader.ReadString('\n')
		if len(line) > 0 {
			currentPos += int64(len(line))

			fmt.Print(line)

			// if we passed the chunk end AND finished a line, stop
			if currentPos >= chunkEnd {
				break
			}
		}

		if err != nil {
			break
		}
	}
}
