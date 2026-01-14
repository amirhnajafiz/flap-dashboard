package interpreter

import (
	"bufio"
	"fmt"
	"os"
	"sort"

	fm "github.com/amirhnajafiz/flak-dashboard/pkg/file_manager"
)

// Interpreter accepts a tracing index directory and starts reading
// the files sequentially to export them as human readable logs.
type Interpreter struct {
	dataDir string

	fdt *fdTable
	vma *virtualMemoryAddressSpace
}

// NewInterpreter returns an interpreter instance.
func NewInterpreter(dataDir string) *Interpreter {
	return &Interpreter{
		dataDir: dataDir,
		fdt: &fdTable{
			kv: make(map[string]map[int]string),
		},
		vma: &virtualMemoryAddressSpace{
			blocks: make(map[string]map[int][]int64),
		},
	}
}

// Start the interpreter
func (i *Interpreter) Start() error {
	// get the file names
	names, err := fm.GetFileNamesByWildcardMatch(i.dataDir, "*.out")
	if err != nil {
		return fmt.Errorf("failed to get file names: %v", err)
	}

	// sort the names
	sort.Strings(names)

	// process each file
	for _, name := range names {
		if err := i.process(fmt.Sprintf("%s/%s", i.dataDir, name)); err != nil {
			return fmt.Errorf("failed processing `%s`: %v", name, err)
		}
	}

	return nil
}

// process a given file.
func (i *Interpreter) process(path string) error {
	file, err := os.Open(path)
	if err != nil {
		return fmt.Errorf("failed to open file `%s`: %v", path, err)
	}
	defer file.Close()

	// create scanner
	scanner := bufio.NewScanner(file)

	// scan the file
	for scanner.Scan() {
		// get each line
		line := scanner.Text()

		fmt.Println(line)
	}

	// check for scanner errors
	if err := scanner.Err(); err != nil {
		return fmt.Errorf("scanner failed: %v", err)
	}

	return nil
}
