package configs

// Default returns a config instance with default values.
func Default() Config {
	return Config{
		DataPath: "data",
		Logger: LoggerConfig{
			Level: "info",
			JSON:  false,
		},
	}
}
