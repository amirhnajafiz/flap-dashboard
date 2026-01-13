package workers

import (
	"os"

	"github.com/amirhnajafiz/flak-dashboard/pkg/models"

	"github.com/sirupsen/logrus"
)

// writer worker submits the events by writing them into files.
// each writer writes into a single file. the number of writers
// is equal to the number of readers, and they match by partition id.
type writer struct {
	path         string
	inputChannel chan models.Packet
}

// start the writer worker.
func (w writer) start() {
	// open the output file.
	fd, err := os.Create(w.path)
	if err != nil {
		logrus.WithFields(logrus.Fields{
			"path":  w.path,
			"error": err,
		}).Error("failed to open file")

		return
	}
	defer fd.Close()

	// get and write trace events into a file
	for pkt := range w.inputChannel {
		if pkt.EOE {
			break
		}

		fd.WriteString(pkt.TraceEventRaw + "\n")
	}
}
