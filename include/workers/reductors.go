package workers

type reductor struct {
	inputChannel   chan string
	writerChannels map[int]chan string
}

func (r reductor) start() {
	for data := range r.inputChannel {
		key := len(data) % len(r.writerChannels)
		r.writerChannels[key] <- data
	}
}
