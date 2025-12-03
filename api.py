from src.api.router import Router
from src.database import Database


def main():
    db = Database("data/data.db")
    router = Router(debug=False, port=5050, db=db)
    router.listen_and_serve()


if __name__ == "__main__":
    main()
