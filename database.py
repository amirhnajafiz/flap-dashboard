# get the logs folder
# read the time references
# open each of three files
# read each line by line
# convert raw time to datetime
# merge enter and exits
import json
import os
import sys

from src.time_reference import generate_datetime_from_nanos
from src.rexfsm import match_string

def main(dir_path: str):
    with open(os.path.join(dir_path, "reference_timestamps.json"), "r") as meta_file:
        meta = json.load(meta_file)
        ref_mono = float(meta['ref_mono'])
        ref_wall = float(meta['ref_wall'])
    
    with open(os.path.join(dir_path, "meta_logs.txt"), "r") as file:
        for line in file:
            m = match_string(line)
            if not m:
                continue
            
            meta = {
                "time": m.group("time"),
                "datetime": generate_datetime_from_nanos(ref_mono, ref_wall, int(m.group("time"))).isoformat(" "), 
                "pid": m.group("pid"),
                "tid": m.group("tid"),
                "proc": m.group("proc")
            }

            status = m.group("status")
            operand = m.group("operand")

            spec_str = m.group("spec")
            spec = {}
            if spec_str.strip():
                for item in spec_str.split():
                    k, v = item.split("=", 1)
                    spec[k] = v

            obj = {
                "meta": meta,
                "status": status,
                "operand": operand,
                "spec": spec
            }

            print(json.dumps(obj, indent=4))

if __name__ == "__main__":
    if len(sys.argv) < 1:
        sys.exit(1)
    
    main(dir_path=sys.argv[1])
