import datetime
import json
import os
import sys


def import_references(dir_path: str) -> tuple[float, float]:
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


def datetime_from_nanos(mono: float, wall: float, input: float) -> datetime.datetime:
    """Accept the mono and wall in nanoseconds and convert the input from nanoseconds to datetime object.

    :param mono:
    :param wall:
    :param input:
    :return datetime.datetime:
    """
    ref_mono_ns = mono * 1e9
    ref_wall_ns = wall * 1e9

    # convert monotonic ns to wall-clock ns
    wall_ns = ref_wall_ns + (input - ref_mono_ns)

    # convert to Python datetime
    dt = datetime.datetime.fromtimestamp(wall_ns / 1e9)

    return dt
