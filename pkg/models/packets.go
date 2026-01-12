package models

// Packet holds critical information for communication
// between workers.
type Packet struct {
	PartitionID int
	Key         string
	Payload     TraceEvent
	Raw         string
}
