import os
import json
from bugster.config.paths import get_credentials_path


def load_credentials():
    creds_file = get_credentials_path()
    if not os.path.exists(creds_file):
        raise FileNotFoundError(
            f"Credentials file not found at {creds_file}. Please provide a valid credentials JSON file."
        )
    with open(creds_file, "r") as f:
        creds = json.load(f)
    return creds
