package main

import (
	"github.com/amirhnajafiz/flak-dashboard/include/bootstrap"
	"github.com/amirhnajafiz/flak-dashboard/include/configs"
	"github.com/amirhnajafiz/flak-dashboard/include/logging"
	"github.com/amirhnajafiz/flak-dashboard/include/workers"

	"github.com/sirupsen/logrus"
)

func main() {
	// load configs
	cfg := configs.LoadConfigs()

	// set the logger
	logging.SetLogger(cfg.Logger.Level, cfg.Logger.JSON)

	// run the bootstrap functions
	files, err := bootstrap.BeginDataLoader(cfg.DataPath, cfg.NumberOfReaders)
	if err != nil {
		panic(err)
	}

	// start the workers for each file sequentially
	wm := workers.NewWorkerManager(cfg.NumberOfReaders, cfg.NumberOfReductors)
	for _, file := range files {
		if err := wm.Run(file); err != nil {
			logrus.WithFields(logrus.Fields{
				"file":  file.Name,
				"error": err,
			}).Panic("worker manager failed")
		}
	}

	// start the interpreters
	if err := bootstrap.StartInterpreter(cfg.DataPath); err != nil {
		logrus.WithField("error", err).Panic("interpretor failed")
	}
}
