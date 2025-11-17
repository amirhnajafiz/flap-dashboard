#!/bin/bash
# file: script.sh

python analysis/create_datasets.py
python analysis/split_traces.py logs/traces.txt traces
python analysis/level_logs.py traces/vllm.log --levels 2
python analysis/plot_traces.py traces/vllm.log
