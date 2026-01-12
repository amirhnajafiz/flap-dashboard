package workers

import "github.com/amirhnajafiz/flak-dashboard/pkg/models"

type reductor struct {
	inputChannel   chan models.Packet
	writerChannels map[int]chan models.Packet
}

func (r reductor) start() {
	for data := range r.inputChannel {
		r.writerChannels[data.PartitionID] <- data
	}
}
