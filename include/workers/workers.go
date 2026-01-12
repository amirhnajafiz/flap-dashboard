package workers

import (
	"fmt"

	"github.com/amirhnajafiz/flak-dashboard/pkg/models"

	"github.com/sirupsen/logrus"
)

// Run the workers.
func Run(
	readers int,
	reductors int,
) {
	// communication channels
	reductorChannels := make(map[int]chan models.Packet, reductors)
	writerChannels := make(map[int]chan models.Packet, readers)

	// start the writers
	for i := range readers {
		channel := make(chan models.Packet)
		writerChannels[i] = channel

		go func(id int, inputChannel chan models.Packet) {
			w := writer{
				path:         fmt.Sprintf("data/%d.out", id),
				inputChannel: inputChannel,
			}
			w.start()
		}(i, channel)
	}

	// start the reductors
	for i := range reductors {
		channel := make(chan models.Packet)
		reductorChannels[i] = channel

		go func(inputChannel chan models.Packet) {
			rd := reductor{
				inputChannel:   inputChannel,
				writerChannels: writerChannels,
			}
			rd.start()
		}(channel)
	}

	// create and call the loader
	l := loader{
		dataPath:         "data",
		numberOfReaders:  readers,
		reductorChannels: reductorChannels,
	}

	logrus.Info("loader start")

	if err := l.begin(); err != nil {
		logrus.Error(err)
	}
}
