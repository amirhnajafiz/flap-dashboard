import sqlite3

from flask import jsonify, make_response

import src.database.queries as queries
from src.database import Database


class Routes:
    """Routes methods will be used as api handler functinos."""

    def __init__(self, db: Database):
        """Routes constructor.

        :param db: Database module
        """
        self.__db = db
    
    def healthz(self):
        """Healthz return 200 on the /healthz endpoint."""
        return make_response("OK", 200)

    def list_io_events(self):
        """List IO events."""
        conn = self.__db.connection()
        conn.row_factory = sqlite3.Row

        cur = conn.cursor()
        cur.execute(queries.GET_IO_LOGS)
        rows = cur.fetchall()

        conn.close()

        return jsonify([dict(row) for row in rows]), 200
