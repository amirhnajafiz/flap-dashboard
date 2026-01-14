package interpreter

import (
	"bufio"
	"fmt"
	"os"
	"sort"
	"strings"

	fm "github.com/amirhnajafiz/flak-dashboard/pkg/file_manager"
)

// Interpreter accepts a tracing index directory and starts reading
// the files sequentially to export them as human readable logs.
type Interpreter struct {
	dataDir        string
	outputFilePath string

	fd *os.File

	handlers map[string]syscallHandlerFunc

	fdt *fdTable
	vma *virtualMemoryAddressSpace
}

// NewInterpreter returns an interpreter instance.
func NewInterpreter(dataDir string, outputFilePath string) *Interpreter {
	// create a new interpreter instance
	i := &Interpreter{
		dataDir:        dataDir,
		outputFilePath: outputFilePath,
		fdt: &fdTable{
			kv: make(map[string]map[int]string),
		},
		vma: &virtualMemoryAddressSpace{
			blocks: make(map[string]map[int][]int64),
		},
	}

	// set the handlers
	i.handlers = map[string]syscallHandlerFunc{
		"open":            i.handleFdTableSyscall,
		"openat":          i.handleFdTableSyscall,
		"statfs":          i.handleFdTableSyscall,
		"statx":           i.handleFdTableSyscall,
		"newlstat":        i.handleFdTableSyscall,
		"newstat":         i.handleFdTableSyscall,
		"creat":           i.handleFdTableSyscall,
		"close":           i.handleFdTableSyscall,
		"dup":             i.handleUpdateFdSyscall,
		"dup2":            i.handleUpdateFdSyscall,
		"dup3":            i.handleUpdateFdSyscall,
		"read":            i.handleIOSyscall,
		"write":           i.handleIOSyscall,
		"readv":           i.handleIOSyscall,
		"writev":          i.handleIOSyscall,
		"pread64":         i.handleIOSyscall,
		"pwrite64":        i.handleIOSyscall,
		"preadv":          i.handleIOSyscall,
		"pwritev":         i.handleIOSyscall,
		"mmap":            i.handleAddressSpaceSyscall,
		"munmap":          i.handleAddressSpaceSyscall,
		"page_fault_user": i.handleMemorySyscall,
	}

	return i
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

	// open the output file
	i.fd, err = os.Create(i.outputFilePath)
	if err != nil {
		return fmt.Errorf("failed to open output file `%s`: %v", i.outputFilePath, err)
	}

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

		// split the line by the line delimeter
		parts := strings.Split(line, "####")
		if len(parts) < 4 {
			continue
		}

		// extract data
		ts := parts[0]
		proc := parts[1]
		event := parts[2]
		kvString := parts[3]

		// build the key-value data
		kv := make(map[string]string)
		for part := range strings.SplitSeq(kvString, "****") {
			if len(part) > 0 {
				data := strings.Split(part, "=")
				if len(data) == 2 {
					kv[strings.Trim(data[0], " ")] = strings.Trim(data[1], " ")
				}
			}
		}

		// call the handler based on the event
		if hd, ok := i.handlers[event]; ok {
			hd(ts, proc, event, kv)
		}
	}

	// check for scanner errors
	if err := scanner.Err(); err != nil {
		return fmt.Errorf("scanner failed: %v", err)
	}

	return nil
}
