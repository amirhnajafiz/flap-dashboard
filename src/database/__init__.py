import logging
import sqlite3
import sys
from sqlite3 import Error

import src.database.queries as queries


class Database:
    def __init__(self, db_path: str):
        self.__db_path = db_path
        self.__conn = None

    def connection(self) -> sqlite3.Connection:
        if self.__conn is not None:
            return self.__conn

        try:
            self.__conn = sqlite3.connect(self.__db_path)
        except Error as e:
            logging.error(f"failed to open database connection {e}")
            sys.exit(1)

        return self.__conn

    def init_tables(self):
        try:
            cursor = self.connection().cursor()
            cursor.execute(queries.CREATE_LOGS_TABLE)
            self.connection().commit()
        except Error as e:
            logging.error(f"failed to create tables {e}")
            sys.exit(1)

    def insert_record(self, batch: list):
        conn = self.connection()
        try:
            conn.executemany(queries.INSERT_LOG_RECORD, batch)
            conn.commit()
        except Error as e:
            logging.error(f"failed to insert records {e}")
            sys.exit(1)
