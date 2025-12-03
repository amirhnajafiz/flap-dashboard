import sys

from src.database import Database
from src.logreaders.io import IOReader
from src.logreaders.meta import MetaReader
from src.utils.files import import_time_references


def main(dir_path: str):
    # read the timestamp references
    ref_mono, ref_wall = import_time_references(dir_path=dir_path)

    # open a database connection and init tables
    db = Database(db_path="data/data.db")
    db.init_tables()

    # create reader instances
    readers = [
        MetaReader(dir_path, ref_mono, ref_wall, db),
        IOReader(dir_path, ref_mono, ref_wall, db),
    ]

    # start readers one by one
    for p in readers:
        p.start()


if __name__ == "__main__":
    if len(sys.argv) < 1:
        sys.exit(1)

    main(dir_path=sys.argv[1])
