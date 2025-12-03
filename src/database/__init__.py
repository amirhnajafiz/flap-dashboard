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
        self.__conn = None

    def connection(self) -> sqlite3.Connection:
        """Connection returns a sqlite3.Connection to sqlite database."""

        if self.__conn is not None:
            return self.__conn

        try:
            self.__conn = sqlite3.connect(self.__db_path)
        except Error as e:
            logging.error(f"failed to open database connection {e}")
            sys.exit(1)

        return self.__conn

    def init_tables(self):
        """Init tables into the sqlite database."""
        try:
            cursor = self.connection().cursor()
            cursor.execute(queries.CREATE_META_LOGS_TABLE)
            cursor.execute(queries.CREATE_IO_LOGS_TABLE)
            self.connection().commit()
        except Error as e:
            logging.error(f"failed to create tables {e}")
            sys.exit(1)

    def insert_records(self, batch: list, query: str):
        """Insert records as batch.

        :param batch: list of objects
        :param query: query to run
        """

        conn = self.connection()

        try:
            conn.executemany(query, batch)
            conn.commit()
        except Error as e:
            logging.error(f"failed to insert records {e}")
            sys.exit(1)
