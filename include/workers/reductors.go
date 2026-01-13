package workers

import "github.com/amirhnajafiz/flak-dashboard/pkg/models"

// reductor worker acts as the event reducer to group, modify, filter
// and submit tracing events.
type reductor struct {
	inputChannel   chan models.Packet
	writerChannels map[int]chan models.Packet
}

// start the reductor worker.
func (r reductor) start() {
	for pkt := range r.inputChannel {
		// check the EOE flag
		if pkt.EOE {
			r.writerChannels[pkt.PartitionIndex] <- pkt
		} else {
			// TODO: group, modify and filter logic
			r.writerChannels[pkt.PartitionIndex] <- pkt
		}
	}
}
