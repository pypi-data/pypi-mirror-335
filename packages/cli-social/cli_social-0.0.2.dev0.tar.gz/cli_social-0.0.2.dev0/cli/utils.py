import os
import json

CONFIG_FILE = os.path.expanduser("~/.cli-social-config")

def load_api_key():
    """Load the API key from the config file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return config.get("api_key")
    return None
