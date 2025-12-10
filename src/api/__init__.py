import os

from flask import Flask

import src.api.views as views
from src.api.routes import Routes
from src.database import Database


class Router:
    """Router is the HTTP handler for our API."""

    def __init__(self, debug: bool, port: int, db: Database, base_dir: str):
        """Router constructor.

        :param debug: flask debug option
        :param port: flask http port
        :param db: database module
        :param base_dir: app base directory
        """
        self.__app = Flask(
            __name__,
            static_folder=os.path.join(base_dir, "static"),
            template_folder=os.path.join(base_dir, "pages"),
        )
        self.__app.config["JSON_SORT_KEYS"] = False
        self.__routes = Routes(db)
        self.__debug = debug
        self.__port = port

    def listen_and_serve(self):
        # define routes
        self.__app.add_url_rule("/", "index", views.index)
        self.__app.add_url_rule("/healthz", "healthz", self.__routes.healthz)
        self.__app.add_url_rule(
            "/api/events/procs", "list_procs", self.__routes.list_procs, methods=["GET"]
        )
        self.__app.add_url_rule(
            "/api/events/io",
            "list_io_events",
            self.__routes.list_io_events,
            methods=["GET"],
        )

        # run the flask app
        self.__app.run(debug=self.__debug, port=self.__port)
