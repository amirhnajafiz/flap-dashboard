import yaml


def load_config(config_path: str = "config.yaml") -> dict:
    """Load application configs from a yaml file.

    :param config_path: config file path (default: "config.yaml")
    """
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    return config
