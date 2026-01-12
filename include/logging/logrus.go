package logging

import "github.com/sirupsen/logrus"

// SetLogger sets the logger using input vars, it defaults to text logs
// on debug level unless otherwise specified.
func SetLogger(level string, jsonLog bool) {
	logrus.SetLevel(logrus.DebugLevel)

	if level != "" {
		llev, err := logrus.ParseLevel(level)
		if err != nil {
			logrus.Fatalf("cannot set LOG_LEVEL to %q", level)
		}

		logrus.SetLevel(llev)
	}

	if jsonLog {
		logrus.SetFormatter(&logrus.JSONFormatter{})
	} else {
		logrus.SetFormatter(&logrus.TextFormatter{
			DisableColors: true,
		})
	}
}
