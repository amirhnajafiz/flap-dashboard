package workers

import "github.com/sirupsen/logrus"

// Run the workers.
func Run(
	readers int,
) {
	// create and call the loader
	l := loader{
		dataPath:        "data",
		numberOfReaders: readers,
	}

	logrus.Info("loader start")

	if err := l.begin(); err != nil {
		logrus.Error(err)
	}
}
