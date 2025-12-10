import logging
import sqlite3
import sys
from sqlite3 import Error

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

import src.database.queries as queries


class BaseModel(DeclarativeBase):
    pass


class NewDatabase:
    def __init__(self, db_path: str):
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False, future=True)

    def session(self):
        return sessionmaker(
            bind=self.engine, autoflush=False, autocommit=False, future=True
        )

    def init_tables(self):
        BaseModel.metadata.create_all(self.engine)

    def raw_execute(self, query: str):
        with self.engine.connect() as conn:
            conn.execute(text(query))


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
            # open a new connection
            conn = self.connection()
            cursor = conn.cursor()

            # create tables
            cursor.execute(queries.CREATE_META_LOGS_TABLE)
            cursor.execute(queries.CREATE_IO_LOGS_TABLE)

            # create indexes
            cursor.execute(queries.CREATE_META_LOGS_INDEX)
            cursor.execute(queries.CREATE_IO_LOGS_INDEX)

            # commit and close
            conn.commit()
            conn.close()
        except Error as e:
            logging.error(f"failed to create tables {e}")
            sys.exit(1)

    def raw_execute(self, query: str):
        """Raw execute a query into the database.

        :param query: a query to run
        """
        try:
            # open a new connection
            conn = self.connection()
            cursor = conn.cursor()

            # execute the query
            cursor.execute(query)

            # commit and close
            conn.commit()
            conn.close()
        except Error as e:
            logging.error(f"failed to execute query \n{query} \n\n\t {e}")
            sys.exit(1)

    def insert_records(self, batch: list, query: str):
        """Insert records as batch.

        :param batch: list of objects
        :param query: query to run
        """

        try:
            # open a new connection
            conn = self.connection()

            # call execute many
            conn.executemany(query, batch)

            # commit and close
            conn.commit()
            conn.close()
        except Error as e:
            logging.error(f"failed to insert records {e}")
            sys.exit(1)
