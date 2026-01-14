package bootstrap

import (
	"fmt"
	"sync"

	"github.com/amirhnajafiz/flak-dashboard/include/components/interpreter"
	tm "github.com/amirhnajafiz/flak-dashboard/pkg/time_manager"

	"github.com/sirupsen/logrus"
)

// StartInterpreter activates two interpreters for processing
// the files inside trace_io_index and trace_memory_index.
func StartInterpreter(dataDirPath string) error {
	var wg sync.WaitGroup
	wg.Add(2)

	// create a time manager
	tmInstance, err := tm.NewTimeManager(dataDirPath + "/reference_timestamps.json")
	if err != nil {
		return fmt.Errorf("failed to create a time manager: %v", err)
	}

	// start the two interpreters instances
	go runInterpreterInstance(fmt.Sprintf("%s/trace_io_chunks", dataDirPath), &wg, tmInstance)
	go runInterpreterInstance(fmt.Sprintf("%s/trace_memory_chunks", dataDirPath), &wg, tmInstance)

	// wait for them to finish
	wg.Wait()

	return nil
}

// run an interpreter instance.
func runInterpreterInstance(path string, wg *sync.WaitGroup, tmInstance *tm.TimeManager) {
	defer wg.Done()

	logrus.WithFields(logrus.Fields{
		"path": path,
	}).Info("interpreter start")

	// create a new interpreter and start
	output := path + "/replay.hrd"
	i := interpreter.NewInterpreter(path, output, tmInstance)

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
