from src.database import Database
from src.logreaders.io import IOReader
from src.logreaders.meta import MetaReader
from src.utils.files import import_time_references


def bootstrap(
    dir_path: str = "logs", enable_import: bool = False, batch_size: int = 100
):
    """Bootstrap starts a init process to create database tables and import the tracing logs.

    :param dir_path: logs directory
    :param enable_import: create database enteties and import the logs into database
    """

    if not enable_import:
        return

    # read the timestamp references
    ref_mono, ref_wall = import_time_references(dir_path=dir_path)

    # open a database connection and init tables
    db = Database(db_path="data/data.db")
    db.init_tables()

    # create reader instances
    readers = [
        MetaReader(dir_path, ref_mono, ref_wall, db, batch_size),
        IOReader(dir_path, ref_mono, ref_wall, db, batch_size),
    ]

    # start readers one by one
    for p in readers:
        p.start()
