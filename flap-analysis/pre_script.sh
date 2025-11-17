#!/bin/bash
# file: pre_script.sh

# global vars
DIR="logs"
DS="datasets"
TRS="traces"
INP="counts.txt"

# remove the old directory
rm -rf $DIR
rm -rf $DS
rm -rf $TRS

# create a new logs directory
mkdir $DIR
mkdir $DS
mkdir $TRS

# take the logs and export it into 4 files
# read_times, read_bytes, write_times, write_bytes
grep -e "read_time" "${INP}" > "${DIR}/read_times.txt"
grep -e "write_time" "${INP}" > "${DIR}/write_times.txt"
grep -e "read_bytes" "${INP}" > "${DIR}/read_bytes.txt"
grep -e "write_bytes" "${INP}" > "${DIR}/write_bytes.txt"
grep -e "read_count" "${INP}" > "${DIR}/read_counts.txt"
grep -e "write_count" "${INP}" > "${DIR}/write_counts.txt"
grep -E '^\[[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}\] (START tracing|[0-9]+ [A-Za-z0-9_-]+ (ENTER|EXIT) (open|openat|read|write|close|dup|dup2))' "$1" > "${DIR}"/traces.txt
