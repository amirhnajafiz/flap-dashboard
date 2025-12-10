import logging

from src.database import Database
from src.database.queries import UPDATE_IO_FNAME_VALUES, UPDATE_FD_FNAME_VALUES
from src.logreaders.io import IOReader
from src.logreaders.meta import MetaReader
from src.utils.files import import_time_references


def bootstrap(
    db: Database,
    dir_path: str = "logs",
    enable_import: bool = False,
    batch_size: int = 100,
):
    """Bootstrap starts a init process to create database tables and import the tracing logs.

    :param dir_path: logs directory
    :param enable_import: create database enteties and import the logs into database
    """

    if not enable_import:
        return

    # init tables
    logging.info("creating tables")
    db.init_tables()
    logging.info("done creating tables")

    # run readers
    __process_readers(db, dir_path, batch_size)

    # update fname values
    logging.info("updating file names")
    db.raw_execute(UPDATE_IO_FNAME_VALUES)
    db.raw_execute(UPDATE_FD_FNAME_VALUES)
    logging.info("done updating file names")


def __process_readers(db: Database, dp: str, bs: int):
    # read the timestamp references
    logging.info("reading references")
    ref_mono, ref_wall = import_time_references(dir_path=dp)
    logging.info("done reading references")

    # create reader instances
    readers = [
        MetaReader(dp, ref_mono, ref_wall, db, bs),
        IOReader(dp, ref_mono, ref_wall, db, bs),
    ]

    logging.info("running log readers")

    # start readers one by one
    for p in readers:
        logging.info(f"starting log reader: {p.name()}")
        p.start()
        logging.info(f"stopping log reader: {p.name()}")

    logging.info("done running log readers")
