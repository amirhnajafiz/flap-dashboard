package models

// TraceEvent models a log entry.
type TraceEvent struct {
	Timestamp int64
	PID       int
	TID       int
	Proc      string
	Event     string
	KV        map[string]string
}
