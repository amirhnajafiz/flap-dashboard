package bootstrap

import (
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"strings"

	"github.com/amirhnajafiz/flak-dashboard/pkg/models"
)

// BeginDataLoader gets the data directory path and creates a list
// of log files that need to be processed by the workers.
func BeginDataLoader(dataDirPath string, numberOfReaders int) ([]*models.File, error) {
	files := make([]*models.File, 0)
	patterns := []string{
		"trace_io_*.log",
		"trace_memory_*.log",
	}

	for _, pattern := range patterns {
		// create the output dir
		outPath := fmt.Sprintf(
			"%s/%s",
			dataDirPath,
			strings.Replace(pattern, "*.log", "index", 1),
		)

		if err := os.MkdirAll(
			outPath,
			os.ModePerm); err != nil {
			return nil, fmt.Errorf("failed to create `%s` directory: %v", pattern, err)
		}

		// get the file names
		fileNames, err := getFilesByWildcardMatch(dataDirPath, pattern)
		if err != nil {
			return nil, fmt.Errorf("failed to read `%s` files: %v", pattern, err)
		}

		for _, name := range fileNames {
			// create a new file model
			file := models.File{
				Name:      name,
				Path:      fmt.Sprintf("%s/%s", dataDirPath, name),
				OutputDir: outPath,
			}

			// get file size
			size, err := getFileSize(file.Path)
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

func getFilesByWildcardMatch(root string, pattern string) ([]string, error) {
	names := make([]string, 0)

	// walk the dir and look for matching patterns
	err := filepath.WalkDir(root, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}

		if d.IsDir() {
			return nil
		}

		if match, err := filepath.Match(pattern, d.Name()); err == nil && match {
			names = append(names, d.Name())
		}

		return nil
	})

	return names, err
}

func getFileSize(path string) (int64, error) {
	// open the log file
	file, err := os.Open(path)
	if err != nil {
		return 0, fmt.Errorf("failed to open the tracing file: %v", err)
	}
	defer file.Close()

	// get the file stat
	info, err := file.Stat()
	if err != nil {
		return 0, fmt.Errorf("failed to get file stat: %v", err)
	}

	return info.Size(), nil
}
