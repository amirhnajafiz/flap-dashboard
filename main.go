package main

import (
	"github.com/amirhnajafiz/flak-dashboard/include/configs"
	"github.com/amirhnajafiz/flak-dashboard/include/logging"
	"github.com/amirhnajafiz/flak-dashboard/include/workers"
)

func main() {
	// load configs
	cfg := configs.LoadConfigs()

	// set the logger
	logging.SetLogger(cfg.Logger.Level, cfg.Logger.JSON)

	// start the workers
	workers.Run(2)
}
