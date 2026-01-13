package main

import (
	"github.com/amirhnajafiz/flak-dashboard/include/bootstrap"
	"github.com/amirhnajafiz/flak-dashboard/include/configs"
	"github.com/amirhnajafiz/flak-dashboard/include/logging"
	"github.com/amirhnajafiz/flak-dashboard/include/workers"
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
	// number of writers is the same as the number of readers
	for _, file := range files {
		workers.Run(cfg.NumberOfReaders, cfg.NumberOfReductors, file)
	}
}
