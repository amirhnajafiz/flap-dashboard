import logging
import os

from src.api.router import Router
from src.bootstrap import bootstrap
from src.configs import load_config
from src.database import Database


def main():
    # load config values from config file
    cfg = load_config()

    # tune the logger
    logging.basicConfig(
        level=getattr(logging, cfg["logging"]["level"].upper()),
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # create a new database instance
    db = Database(cfg["database"]["path"])

    # call bootstrap function
    logging.info("calling bootstrap")
    bootstrap(
        db,
        cfg["bootstrap"]["logs_path"],
        cfg["bootstrap"]["enable"],
        cfg["bootstrap"]["batch_size"],
    )

    # find the base dir for templates
    base_dir = os.path.join(os.path.dirname(__file__), "templates")

    logging.info("starting flask router")

    # create a new router and start
    router = Router(
        debug=cfg["api"]["debug"], port=cfg["api"]["port"], db=db, base_dir=base_dir
    )
    router.listen_and_serve()


if __name__ == "__main__":
    main()
