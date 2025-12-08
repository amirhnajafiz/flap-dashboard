import sqlite3

from flask import jsonify

import src.database.queries as queries
from src.database import Database


class Routes:
    def __init__(self, db: Database):
        self.__db = db

    def list_events(self):
        conn = self.__db.connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(queries.GET_IO_EVENTS)
        rows = cur.fetchall()
        conn.close()

        return jsonify([dict(row) for row in rows]), 200

    def list_files(self):
        pass

    def list_latencies(self):
        pass
