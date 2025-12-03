from flask import Flask

from src.database import Database
from src.api.routes import Routes


class Router:
    def __init__(self, debug: bool, port: int, db: Database):
        self.__app = Flask(
            __name__,
            static_folder="templates/static",
            template_folder="templates/pages",
        )
        self.__app.config["JSON_SORT_KEYS"] = False
        self.__routes = Routes(db)
        self.__debug = debug
        self.__port = port

    def listen_and_serve(self):
        # define routes
        self.__app.add_url_rule(
            "/api/events", "list_events", self.__routes.list_events, methods=["GET"]
        )
        self.__app.add_url_rule(
            "/api/files", "list_files", self.__routes.list_files, methods=["GET"]
        )
        self.__app.add_url_rule(
            "/api/latencies", "list_latencies", self.__routes.list_latencies, methods=["GET"]
        )

        # run the flask app
        self.__app.run(debug=self.__debug, port=self.__port)
