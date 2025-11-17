#!/usr/bin/env python3
import re
import sys
from pathlib import Path
from collections import defaultdict



# Usage: ./split_traces.py input.log [output_dir]

if len(sys.argv) < 2:
    print("Usage: ./split_traces.py <input.log> [output_dir]")
    sys.exit(1)

input_file = Path(sys.argv[1])
output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("split_logs")
output_dir.mkdir(exist_ok=True)

# regex pattern for lines with commands like "3586860 vllm ENTER ..."
log_pattern = re.compile(
    r'^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]\s+\d+\s+([A-Za-z0-9_-]+)\s+(ENTER|EXIT)\s+\w+'
)

# collect lines per command name
logs_by_cmd = defaultdict(list)

with input_file.open("r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        match = log_pattern.match(line)
        if match:
            cmd = match.group(1)
            logs_by_cmd[cmd].append(line)

# write to separate files
for cmd, lines in logs_by_cmd.items():
    outfile = output_dir / f"{cmd}.log"
    with outfile.open("w", encoding="utf-8") as out:
        out.writelines(lines)
    print(f"wrote {len(lines)} lines to {outfile}")

print(f"\nAll logs saved in: {output_dir.resolve()}")
