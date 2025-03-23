import os
from nati.config import load_config

config_path = "./nati.ini"


def main():
    print("Welcome to NATI\n")
    print("Validating config file (nati.ini)...\n")
    check_config()


def check_config():
    if not os.path.exists(config_path):
        print("Configuration file not found.")
        print(
            "Please run 'generate_config.py' to create a default configuration.\n"
        )
        return False

    try:
        config = load_config()
        print("Configuration file exists and is valid.")
        return True
    except Exception as e:
        print(f"Error validating configuration: {str(e)}")
        return False


if __name__ == "__main__":
    main()
