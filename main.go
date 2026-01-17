package main

import (
	"github.com/amirhnajafiz/flak-dashboard/include/cmd"
	"github.com/amirhnajafiz/flak-dashboard/include/configs"
	"github.com/amirhnajafiz/flak-dashboard/include/logging"

	"github.com/spf13/cobra"
)

func main() {
	// load configs
	cfg := configs.LoadConfigs()

	// set the logger
	logging.SetLogger(cfg.Logger.Level, cfg.Logger.JSON)

	// create cobra root command
	root := &cobra.Command{}
	root.AddCommand(
		cmd.LoaderCMD{Cfg: *cfg}.Command(),
		cmd.InterpreterCMD{Cfg: *cfg}.Command(),
	)

	// execute the requested command
	if err := root.Execute(); err != nil {
		panic(err)
	}
}
