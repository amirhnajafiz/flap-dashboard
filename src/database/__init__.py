import logging
import sqlite3
import sys
from sqlite3 import Error

import src.database.queries as queries


class Database:
    """Database module connects to the sqlite database and provides the
    interface for data management.
    """

    def __init__(self, db_path: str):
        """Database constructor.

        :param db_path: Path to sqlite file.
        """
        self.__db_path = db_path

    def connection(self) -> sqlite3.Connection:
        """Connection returns a sqlite3.Connection to sqlite database."""

        conn = None
        try:
            conn = sqlite3.connect(self.__db_path)
        except Error as e:
            logging.error(f"failed to open database connection {e}")
            sys.exit(1)

        return conn

    def init_tables(self):
        """Init tables into the sqlite database."""
        try:
            conn = self.connection()
            cursor = conn.cursor()

            # create tables
            cursor.execute(queries.CREATE_META_LOGS_TABLE)
            cursor.execute(queries.CREATE_IO_LOGS_TABLE)

            conn.commit()
            conn.close()
        except Error as e:
            logging.error(f"failed to create tables {e}")
            sys.exit(1)

    def insert_records(self, batch: list, query: str):
        """Insert records as batch.

        :param batch: list of objects
        :param query: query to run
        """

        try:
            conn = self.connection()
            conn.executemany(query, batch)
            conn.commit()
            conn.close()
        except Error as e:
            logging.error(f"failed to insert records {e}")
            sys.exit(1)
