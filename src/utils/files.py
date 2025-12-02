import json
import os
import sys


def import_time_references(dir_path: str) -> tuple[float, float]:
    try:
        with open(
            os.path.join(dir_path, "reference_timestamps.json"), "r"
        ) as meta_file:
            meta = json.load(meta_file)
            ref_mono = float(meta["ref_mono"])
            ref_wall = float(meta["ref_wall"])

            return ref_mono, ref_wall
    except Exception as e:
        print(f"failed to import references: {e}")
        sys.exit(1)
