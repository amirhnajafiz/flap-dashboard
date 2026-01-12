package workers

import (
	"bufio"
	"fmt"
	"io"
	"os"

	"github.com/sirupsen/logrus"
)

// reader gets a file, offset, and chunkSize to read
// a partition of a file and pass it's lines to the reader-reductor
// distributor.
type reader struct {
	// unique id of the partition of the file
	id int

	// read parameters
	offset    int64
	chunkSize int64
	fileSize  int64

	// target file
	filePath string
}

// start the reader worker.
func (r reader) start() {
	// open the log file
	fd, err := os.Open(r.filePath)
	if err != nil {
		logrus.WithFields(logrus.Fields{
			"id":    r.id,
			"error": err,
			"path":  r.filePath,
		}).Error("failed to open the target file")

		return
	}
	defer fd.Close()

	logrus.WithFields(
		logrus.Fields{
			"id":    r.id,
			"start": r.offset,
			"end":   r.offset + r.chunkSize,
		},
	).Info("reader start")

	// seek to chunk start
	_, err = fd.Seek(r.offset, io.SeekStart)
	if err != nil {
		logrus.WithFields(logrus.Fields{
			"id":    r.id,
			"error": err,
			"path":  r.filePath,
		}).Error("seek to chunk start failed")

		return
	}

	// create a reader of 64Kb size
	reader := bufio.NewReaderSize(fd, 64*1024)

	// set the parameters
	chunkEnd := r.offset + r.chunkSize
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

			// if we passed the chunk end and finished a line, stop
			if currentPos >= chunkEnd {
				break
			}
		}

		if err != nil {
			break
		}
	}
}
