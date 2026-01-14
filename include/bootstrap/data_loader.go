package bootstrap

import (
	"fmt"
	"os"
	"strings"

	fm "github.com/amirhnajafiz/flak-dashboard/pkg/file_manager"
	"github.com/amirhnajafiz/flak-dashboard/pkg/models"
)

// BeginDataLoader gets the data directory path and returns a list
// of log files that need to be processed by the workers.
func BeginDataLoader(dataDirPath string, numberOfReaders int) ([]*models.File, error) {
	// array of files to be returned
	files := make([]*models.File, 0)

	// patterns
	patterns := []string{
		"trace_io_*.log",
		"trace_memory_*.log",
	}

	// for each pattern get the file names and build a file instance
	for _, pattern := range patterns {
		// create the output dir
		outPath := fmt.Sprintf(
			"%s/%s",
			dataDirPath,
			strings.Replace(pattern, "*.log", "chunks", 1),
		)

		if err := os.MkdirAll(
			outPath,
			os.ModePerm); err != nil {
			return nil, fmt.Errorf("failed to create `%s` directory: %v", pattern, err)
		}

		// get the file names
		fileNames, err := fm.GetFileNamesByWildcardMatch(dataDirPath, pattern)
		if err != nil {
			return nil, fmt.Errorf("failed to read `%s` files: %v", pattern, err)
		}

		for index, name := range fileNames {
			// create a new file model
			file := models.File{
				Id:        index,
				Name:      name,
				Path:      fmt.Sprintf("%s/%s", dataDirPath, name),
				OutputDir: outPath,
			}

			// get file size
			size, err := fm.GetFileSize(file.Path)
			if err != nil {
				return nil, fmt.Errorf("failed to get file `%s` stats: %v", file.Path, err)
			}

			file.FileSize = size
			file.ChunkSize = int(size / int64(numberOfReaders))

			// store the file
			files = append(files, &file)
		}
	}

	return files, nil
}
