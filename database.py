# get the logs folder
# read the time references
# open each of three files
# read each line by line
# convert raw time to datetime
# merge enter and exits
import sys


from src.logreaders.events import EventsReader
from src.logreaders.io import IOReader
from src.logreaders.meta import MetaReader
from src.time_reference import import_references


def main(dir_path: str):
    ref_mono, ref_wall = import_references(dir_path=dir_path)

    parsers = [
        EventsReader(dir_path, ref_mono, ref_wall),
        IOReader(dir_path, ref_mono, ref_wall),
        MetaReader(dir_path, ref_mono, ref_wall)
    ]

    for p in parsers:
        p.parse()


if __name__ == "__main__":
    if len(sys.argv) < 1:
        sys.exit(1)

    main(dir_path=sys.argv[1])
