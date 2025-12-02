import sqlite3

class Connector:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path, timeout=10)

    def insert(self, query: str):
        pass