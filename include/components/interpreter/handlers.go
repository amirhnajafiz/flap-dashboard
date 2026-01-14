package interpreter

import (
	"fmt"
	"strconv"
)

type handlerFunc func(string, string, string, map[string]string)

func (i *Interpreter) handleIOSyscall(ts, proc, operand string, kv map[string]string) {
	ret, _ := strconv.Atoi(kv["ret"])
	fd, _ := strconv.Atoi(kv["fd"])

	if ret < 0 {
		return
	}

	fname := i.fdt.search(proc, fd)
	if len(fname) == 0 {
		fname = fmt.Sprintf("unknown (fd=%d)", fd)
	}

	fmt.Printf("%s [%s : %s] on: %s\n", ts, proc, operand, fname)
}

func (i *Interpreter) handleMemorySyscall(ts, proc, operand string, kv map[string]string) {}

func (i *Interpreter) handleAddressSpaceSyscall(ts, proc, operand string, kv map[string]string) {}

func (i *Interpreter) handleFdTableSyscall(ts, proc, operand string, kv map[string]string) {
	ret, _ := strconv.Atoi(kv["ret"])
	if ret < 0 {
		return
	}

	if operand == "close" {
		fd, _ := strconv.Atoi(kv["fd"])
		i.fdt.remove(proc, fd)
	} else {
		i.fdt.put(proc, ret, kv["fname"])
	}
}

func (i *Interpreter) handleUpdateFdSyscall(ts, proc, operand string, kv map[string]string) {}
