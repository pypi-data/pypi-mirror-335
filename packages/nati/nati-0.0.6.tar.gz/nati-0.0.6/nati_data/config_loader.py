import configparser
import os

def load_project_config(filename="nati.ini"):
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    config_path = os.path.join(base_path, filename)

    print(f"[DEBUG] Reading config from: {config_path}")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at {config_path}")

    config = configparser.ConfigParser()

    with open(config_path, 'r', encoding='utf-8') as f:
        config.read_file(f)

    if "database" not in config:
        raise ValueError("Missing [database] section in config")

    print("[DEBUG] Config loaded:", dict(config["database"]))
    return config["database"]
