package bootstrap

import (
	"fmt"
	"sync"

	"github.com/amirhnajafiz/flak-dashboard/include/components/interpreter"

	"github.com/sirupsen/logrus"
)

// StartInterpreter activates two interpreters for processing
// the files inside trace_io_index and trace_memory_index.
func StartInterpreter(dataDirPath string) {
	var wg sync.WaitGroup
	wg.Add(2)

	// start two interpreters instances
	go func(subdir string) {
		defer wg.Done()
		runInstance(dataDirPath, subdir)
	}("trace_io_index")
	go func(subdir string) {
		defer wg.Done()
		runInstance(dataDirPath, subdir)
	}("trace_memory_index")

	// wait for them to finish
	wg.Wait()
}

// run an interpreter instance.
func runInstance(dataDirPath string, subdir string) {
	path := fmt.Sprintf("%s/%s", dataDirPath, subdir)

	// create a new interpreter and start
	i := interpreter.NewInterpreter(path)
	if err := i.Start(); err != nil {
		logrus.WithFields(logrus.Fields{
			"name":  subdir,
			"error": err,
		}).Panic("interpreter failed")
	}
}
