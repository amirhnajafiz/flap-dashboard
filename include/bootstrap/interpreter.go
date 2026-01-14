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
	wg.Add(1)

	// start the two interpreters instances
	go runInterpreterInstance(fmt.Sprintf("%s/trace_io_index", dataDirPath), &wg)
	//go runInterpreterInstance(fmt.Sprintf("%s/trace_memory_index", dataDirPath), &wg)

	// wait for them to finish
	wg.Wait()
}

// run an interpreter instance.
func runInterpreterInstance(path string, wg *sync.WaitGroup) {
	defer wg.Done()

	logrus.WithFields(logrus.Fields{
		"path": path,
	}).Info("interpreter start")

	// create a new interpreter and start
	i := interpreter.NewInterpreter(path)

	// check for any internal errors
	if err := i.Start(); err != nil {
		logrus.WithFields(logrus.Fields{
			"path":  path,
			"error": err,
		}).Panic("interpreter failed")
	}

	logrus.WithFields(logrus.Fields{
		"path": path,
	}).Info("interpreter finished")
}
