package workers

import (
	"bufio"
	"fmt"
	"io"
	"os"
	"regexp"
	"strconv"
	"strings"

	"github.com/amirhnajafiz/flak-dashboard/pkg/models"

	"github.com/sirupsen/logrus"
)

var (
	re = regexp.MustCompile(`^(\d+)\s+\{pid=(\d+)\s+tid=(\d+)\s+proc=([^\}]+)\}\{(EN|EX)\s+([^\}]+)\}(?:\{([^\}]*)\})?$`)
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

	// reductor channels
	reductorChannels map[int]chan models.Packet
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

			// call the log handler
			r.logHandler(line)

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

// In log handler, match with the regex and skip if not matched.
// Else, extract and build the transfer packet [PartitionID, Key (proc, pid, tid), TS, Payload]
// and send it to the distributor.
func (r reader) logHandler(line string) {
	line = strings.TrimSpace(line)
	match := re.FindStringSubmatch(line)
	if match == nil {
		return
	}

	timestamp, _ := strconv.ParseInt(match[1], 10, 64)
	pid, _ := strconv.Atoi(match[2])
	tid, _ := strconv.Atoi(match[3])

	// parse the key-value block
	kv := make(map[string]string)
	parts := strings.Split(match[6], " ")
	for _, part := range parts {
		kvPair := strings.SplitN(part, "=", 2)
		if len(kvPair) == 2 {
			kv[kvPair[0]] = kvPair[1]
		}
	}

	// create a new event
	event := models.TraceEvent{
		Timestamp: timestamp,
		PID:       pid,
		TID:       tid,
		Proc:      match[4],
		Event:     match[5],
		KV:        kv,
	}

	// create a packet
	pkt := models.Packet{
		PartitionID: r.id,
		Key:         fmt.Sprintf("%d-%d-%s", event.PID, event.TID, event.Proc),
		Payload:     event,
		Raw:         line,
	}

	// find the reductor
	index := len(pkt.Key) % len(r.reductorChannels)
	r.reductorChannels[index] <- pkt
}
