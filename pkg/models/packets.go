package models

// Packet holds critical information for communication between workers.
type Packet struct {
	// End of events flag
	EOE bool
	// Partition data
	PartitionIndex int
	PartitionName  string
	// Trace data
	TraceKey      string
	TraceEventRaw string
	TraceEvent    TraceEvent
}
