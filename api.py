import os

from src.api.router import Router
from src.database import Database


def main():
    db = Database("data/data.db")
    base_dir = os.path.join(os.path.dirname(__file__), "templates")

    router = Router(debug=False, port=5050, db=db, base_dir=base_dir)
    router.listen_and_serve()


if __name__ == "__main__":
    main()
