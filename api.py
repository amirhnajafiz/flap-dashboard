import sqlite3

from src.database import Database
import src.database.queries as queries


def main():
    db = Database("data/data.db")

    conn = db.connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    print("=== REAL SQL ===")
    print(queries.GET_IO_EVENTS)
    print("================")
    cur.execute(queries.GET_IO_EVENTS)
    rows = cur.fetchall()
    conn.close()

    return [dict(row) for row in rows]

if __name__ == "__main__":
    for row in main():
        print(row)
