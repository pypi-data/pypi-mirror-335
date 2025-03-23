import configparser
import os

CONFIG_PATHS = [
    "./nati.ini",                           # Project directory (for development)
    os.path.expanduser("~/.nati/nati.ini"),  # Home directory (preferred)
    "/etc/nati/nati.ini",                    # System-wide config (Linux)
]

def load_config():
    """Load configuration from the first available config file."""
    config = configparser.ConfigParser()
    
    for path in CONFIG_PATHS:
        if os.path.exists(path):
            config.read(path)
            return config
    
    raise FileNotFoundError(
        "No valid configuration file found. Run 'python generate_config.py' to create one."
    )

# Example usage
if __name__ == "__main__":
    config = load_config()
    print(f"Loaded configuration from {CONFIG_PATHS}")
