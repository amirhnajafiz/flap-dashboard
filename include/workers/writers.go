package workers

import (
	"os"

	"github.com/amirhnajafiz/flak-dashboard/pkg/models"

	"github.com/sirupsen/logrus"
)

type writer struct {
	path         string
	inputChannel chan models.Packet
}

func (w writer) start() {
	fd, err := os.Create(w.path)
	if err != nil {
		logrus.WithFields(logrus.Fields{
			"path":  w.path,
			"error": err,
		}).Error("failed to open file")

		return
	}
	defer fd.Close()

	for data := range w.inputChannel {
		fd.WriteString(data.Raw + "\n")
	}
}
