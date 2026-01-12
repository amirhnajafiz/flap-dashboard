package configs

// Default returns a config instance with default values.
func Default() Config {
	return Config{
		NumberOfReaders: 4,
		DataPath:        "data",
		Logger: LoggerConfig{
			Level: "info",
			JSON:  false,
		},
	}
}
