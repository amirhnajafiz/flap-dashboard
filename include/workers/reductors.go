package workers

import "fmt"

type reductor struct {
	inputChannel   chan string
	writerChannels map[int]chan string
}

func (r reductor) start() {
	for data := range r.inputChannel {
		fmt.Println(data)
	}
}
