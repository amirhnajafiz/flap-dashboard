import logging
import sys

from sqlalchemy import Connection, create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class BaseModel(DeclarativeBase):
    """Base model is a sqlalchemy declarative base model."""

    pass


class Database:
    """Database module uses sqlalchemy orm to provide database interface."""

    def __init__(self, db_path: str):
        """In constructor method, a new database engine is created.

        :param db_path: path to sqlite database file.
        """
        self._db_path = db_path
        self._engine = create_engine(f"sqlite:///{db_path}", echo=False, future=True)

    def new_connection(self) -> Connection:
        """New connections opens and returns a new database connection."""
        try:
            return self._engine.connect()
        except SQLAlchemyError as e:
            logging.error(f"failed to open a new connection: {e}")
            sys.exit(1)

    def new_session(self) -> sessionmaker:
        """New session creates a new session using the existing sqlite engine."""
        try:
            return sessionmaker(
                bind=self._engine, autoflush=False, autocommit=False, future=True
            )
        except SQLAlchemyError as e:
            logging.error(f"failed to open a new session: {e}")
            sys.exit(1)

    def init_tables(self):
        """Init tables into the sqlite database."""
        try:
            BaseModel.metadata.create_all(self._engine)
        except SQLAlchemyError as e:
            logging.error(f"failed to create tables: {e}")
            sys.exit(1)

    def batch_insert(self, records: list[any]):
        """Batch insert accepts a list of records to insert.

        :param records: list of records to insert
        """
        try:
            with self.new_session().begin() as session:
                session.bulk_save_objects(records)
                session.commit()
        except SQLAlchemyError as e:
            logging.error(f"failed to insert batch: {e}")
            sys.exit(1)

    def raw_execute(self, query: str):
        """Raw execute a query into the database.

        :param query: a query to run
        """
        try:
            with self._engine.connect() as conn:
                conn.execute(text(query))
                conn.commit()
        except SQLAlchemyError as e:
            logging.error(f"failed to execute query {e}:\n'\n{query}\n'\n")
            sys.exit(1)
