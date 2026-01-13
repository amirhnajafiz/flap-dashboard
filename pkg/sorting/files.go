package sorting

import (
	"fmt"
	"os"
	"os/exec"
)

// sort a target file by calling cort command.
func SortFile(filePath string) error {
	// run Linux sort command
	cmd := exec.Command("sort", filePath, "-o", filePath)

	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	if err := cmd.Run(); err != nil {
		return fmt.Errorf("failed to sort file: %v", err)
	}

	return nil
}
