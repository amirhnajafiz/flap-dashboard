#!/usr/bin/env python3
import fnmatch
import re
import sys
import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import defaultdict


# Usage:
#   ./level_logs.py <logfile> [--levels N]

if len(sys.argv) < 2:
    print("Usage: ./level_logs.py <logfile> [--levels N]")
    sys.exit(1)

log_file = Path(sys.argv[1])
levels = 1

if "--levels" in sys.argv:
    idx = sys.argv.index("--levels")
    if idx + 1 < len(sys.argv):
        levels = int(sys.argv[idx + 1])

pattern = re.compile(
    r'^\[(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\].*?\bfname=(?P<file>[^\s]+)'
)
ex_patterns = [
    "/cpu*", "/vulnerabilities*", "/bus*", "/dev*", "/etc*", "/__pycache__*",
    "/proc*", "/sys*", "/self*", "/sbin*", "/dispatching*", "/kernel*", "/tmp*",
    "/online*", "/possible*", "/present*"
]


def get_prefix(path: str, levels: int = 3) -> str:
    parts = path.strip().split('/')
    if parts and parts[0] == '':
        parts = parts[1:]
    return "/" + "/".join(parts[:levels]) if parts else path


print("[info] Parsing log file...")
prefix_times = defaultdict(lambda: defaultdict(int))

with log_file.open("r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        m = pattern.search(line)
        if not m:
            continue
        t = datetime.strptime(m.group("time"), "%Y-%m-%d %H:%M:%S")
        t = t.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("America/New_York"))
        prefix = get_prefix(m.group("file"), levels)
        if any(fnmatch.fnmatch(prefix, p) for p in ex_patterns):
            continue

        # round time to second-level granularity
        time_key = t.strftime("%Y-%m-%d %H:%M:%S")
        prefix_times[prefix][time_key] += 1

# convert defaultdicts to normal dicts for JSON export
prefix_times = {k: dict(v) for k, v in prefix_times.items()}

# print JSON output
with open(f"{log_file}.json", "w") as file:
    json.dump(prefix_times, file, indent=2, sort_keys=True)
