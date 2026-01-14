package interpreter

import (
	"fmt"
	"strconv"
)

type handlerFunc func(string, string, string, map[string]string)

func (i *Interpreter) handleIOSyscall(ts, proc, operand string, kv map[string]string) {
	ret, _ := strconv.Atoi(kv["ret"])
	if ret < 0 {
		return
	}

	fd, _ := strconv.Atoi(kv["fd"])

	fname := i.fdt.search(proc, fd)
	if len(fname) == 0 {
		fname = fmt.Sprintf("unknown (fd=%d)", fd)
	}

	fmt.Printf("%s+%s [%s : %s] %s bytes file: %s\n", ts, kv["diff"], proc, operand, fname, kv["count"])
}

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

func (i *Interpreter) handleUpdateFdSyscall(ts, proc, operand string, kv map[string]string) {
	ret, _ := strconv.Atoi(kv["ret"])
	if ret < 0 {
		return
	}

	newFd, _ := strconv.Atoi(kv["newfd"])
	oldFd, _ := strconv.Atoi(kv["oldfd"])

	i.fdt.replace(proc, oldFd, newFd)
}

func (i *Interpreter) handleMemorySyscall(ts, proc, operand string, kv map[string]string) {
	ret, _ := strconv.Atoi(kv["ret"])
	if ret < 0 {
		return
	}

	address, _ := strconv.ParseInt(kv["addr"], 10, 64)
	fd := i.vma.search(proc, address)

	fname := i.fdt.search(proc, fd)
	if len(fname) == 0 {
		fname = fmt.Sprintf("unknown (fd=%d)", fd)
	}

	fmt.Printf("%s+%s [%s : %s] memory_access: %s\n", ts, kv["diff"], proc, operand, fname)
}

func (i *Interpreter) handleAddressSpaceSyscall(ts, proc, operand string, kv map[string]string) {
	ret, _ := strconv.Atoi(kv["ret"])
	if ret < 0 {
		return
	}

	address, _ := strconv.ParseInt(kv["addr"], 10, 64)
	boundary, _ := strconv.ParseInt(kv["len"], 10, 64)

	if operand == "mmap" {
		fd, _ := strconv.Atoi(kv["fd"])
		i.vma.put(proc, fd, address, boundary)
	} else {
		fd := i.vma.search(proc, address)
		if fd > -1 {
			i.vma.remove(proc, fd)
		}
	}
}
