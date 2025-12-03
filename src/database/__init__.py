import logging
import sqlite3
import sys
from sqlite3 import Error

import src.database.queries as queries


class Database:
    def __init__(self, db_path: str):
        self.__db_path = db_path
        self.__conn = None
        self.__query_map = {
            "meta": queries.INSERT_META_LOG_RECORD,
            "io": queries.INSERT_IO_LOG_RECORD
        }

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
            cursor.execute(queries.CREATE_META_LOGS_TABLE)
            cursor.execute(queries.CREATE_IO_LOGS_TABLE)
            self.connection().commit()
        except Error as e:
            logging.error(f"failed to create tables {e}")
            sys.exit(1)

    def insert_records(self, batch: list, query_type: str):
        conn = self.connection()
        query = self.__query_map[query_type]

        try:
            conn.executemany(query, batch)
            conn.commit()
        except Error as e:
            logging.error(f"failed to insert records {e}")
            sys.exit(1)
