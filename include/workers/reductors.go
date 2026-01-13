package workers

import (
	"fmt"
	"maps"
	"sync"

	"github.com/amirhnajafiz/flak-dashboard/pkg/models"
)

// reductor worker acts as the event reducer to group, modify, filter
// and submit tracing events.
type reductor struct {
	memory map[string]*models.Packet

	terminationChannel chan int
	inputChannel       chan models.Packet
	writerChannels     map[int]chan models.Packet

	readerReductorInFlightWg *sync.WaitGroup
	reductorWriterInFlightWg *sync.WaitGroup
}

// start the reductor worker.
func (r *reductor) start() {
	for {
		select {
		case <-r.terminationChannel:
			return
		case pkt := <-r.inputChannel:
			r.readerReductorInFlightWg.Done()

			// check if there is a match
			if val, ok := r.memory[pkt.TraceKey]; ok {
				var mPkt *models.Packet
				if val.TraceEvent.EventType == "EN" {
					mPkt = r.merge(val, &pkt)
				} else {
					mPkt = r.merge(&pkt, val)
				}

				r.reductorWriterInFlightWg.Add(1)
				r.writerChannels[mPkt.PartitionIndex] <- *mPkt

				delete(r.memory, pkt.TraceKey)
			} else {
				// save the packet into memory if no match
				r.memory[pkt.TraceKey] = &pkt
			}
		}
	}
}

// merge two trace events and place the results in the start packet.
func (r *reductor) merge(start *models.Packet, end *models.Packet) *models.Packet {
	// calculate the difference
	diff := end.TraceEvent.Timestamp - start.TraceEvent.Timestamp
	start.TraceEvent.KV["diff"] = fmt.Sprintf("%d", diff)

	// merge the key values
	maps.Copy(start.TraceEvent.KV, end.TraceEvent.KV)

	return start
}
