package workers

import "github.com/sirupsen/logrus"

func Run(
	readers int,
) {
	// create and call the loader
	l := loader{
		dataPath:        "data",
		numberOfReaders: 5,
	}
	if err := l.begin(); err != nil {
		logrus.Error(err)
	}
}
