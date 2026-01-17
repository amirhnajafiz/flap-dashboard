package main

import (
	"github.com/amirhnajafiz/flak-dashboard/include/bootstrap"
	"github.com/amirhnajafiz/flak-dashboard/include/components/loader"
	"github.com/amirhnajafiz/flak-dashboard/include/configs"
	"github.com/amirhnajafiz/flak-dashboard/include/logging"

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

	// create a loader coordinator
	coor := loader.Coordinator{
		Readers:   cfg.NumberOfReaders,
		Reductors: cfg.NumberOfReductors,
		Writers:   cfg.NumberOfReaders,
	}

	// start loading the data for each file sequentially
	for _, file := range files {
		if err := coor.Begin(file); err != nil {
			logrus.WithFields(logrus.Fields{
				"file":  file.Name,
				"error": err,
			}).Panic("coordinator failed")
		}
	}

	// start the interpreters
	if err := bootstrap.StartInterpreter(cfg.DataPath); err != nil {
		logrus.WithField("error", err).Panic("interpretor failed")
	}
}
