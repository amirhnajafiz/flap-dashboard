import json
import logging
import os
import sys
from pathlib import Path


def import_time_references(dir_path: str) -> tuple[float, float]:
    """Import time reference from reference_timestamps.json in the logs directory.

    :param dir_path: the logs directory
    :return float: reference mono
    :return float: reference wall
    """
    try:
        with open(
            os.path.join(dir_path, "reference_timestamps.json"), "r"
        ) as meta_file:
            meta = json.load(meta_file)
            ref_mono = float(meta["ref_mono"])
            ref_wall = float(meta["ref_wall"])

            return ref_mono, ref_wall
    except Exception as e:
        logging.error(f"failed to import references: {e}")
        sys.exit(1)


def list_files_by_regex(path: str, regex: str) -> list[str]:
    """List files by a given regex from a directory path.

    :param path: input directory path
    :param regex: regex to filter
    """
    root = Path(path)
    return [x for x in root.rglob(regex)]
