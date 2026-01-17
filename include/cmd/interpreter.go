package cmd

import (
	"fmt"
	"sync"

	"github.com/amirhnajafiz/flak-dashboard/include/components/interpreter"
	"github.com/amirhnajafiz/flak-dashboard/include/configs"
	"github.com/amirhnajafiz/flak-dashboard/pkg/time_manager"

	"github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
)

type InterpreterCMD struct {
	Cfg configs.Config
}

func (i InterpreterCMD) Command() *cobra.Command {
	return &cobra.Command{
		Use:   "interpreter",
		Short: "interpreting-data-chunks",
		Long:  "Interpreter reads the data chunks created by loader and builds a human readable log file",
		Run:   i.main,
	}
}

func (i InterpreterCMD) main(_ *cobra.Command, _ []string) {
	var wg sync.WaitGroup
	wg.Add(2)

	// create a time manager
	tmInstance, err := time_manager.NewTimeManager(i.Cfg.DataPath + "/reference_timestamps.json")
	if err != nil {
		panic(err)
	}

	// start the two interpreters instances
	go i.runInterpreterInstance(fmt.Sprintf("%s/trace_io_chunks", i.Cfg.DataPath), &wg, tmInstance)
	go i.runInterpreterInstance(fmt.Sprintf("%s/trace_memory_chunks", i.Cfg.DataPath), &wg, tmInstance)

	// wait for them to finish
	wg.Wait()
}

// run an interpreter instance.
func (i *InterpreterCMD) runInterpreterInstance(path string, wg *sync.WaitGroup, tmInstance *time_manager.TimeManager) {
	defer wg.Done()

	logrus.WithFields(logrus.Fields{
		"path": path,
	}).Info("interpreter start")

	// create a new interpreter and start
	output := path + "/replay.hrd"
	ii := interpreter.NewInterpreter(path, output, tmInstance)

	// check for any internal errors
	if err := ii.Start(); err != nil {
		logrus.WithFields(logrus.Fields{
			"path":  path,
			"error": err,
		}).Panic("interpreter failed")
	}

	logrus.WithFields(logrus.Fields{
		"path": path,
	}).Info("interpreter finished")
}
