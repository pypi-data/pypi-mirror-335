import os
from typing import Dict
from dotenv import load_dotenv

SINGLESTORE_API_KEY = ""
SINGLESTORE_API_BASE_URL = "https://api.singlestore.com"
SINGLESTORE_DB_USERNAME = ""
SINGLESTORE_DB_PASSWORD = ""


def load_config():
    """Load and validate environment variables."""
    global SINGLESTORE_API_KEY, SINGLESTORE_API_BASE_URL
    global SINGLESTORE_DB_USERNAME, SINGLESTORE_DB_PASSWORD

    load_dotenv()

    value = os.getenv("SINGLESTORE_API_KEY")
    if value is None or value.strip() == "":
        raise EnvironmentError(
            "Missing required environment variable: SINGLESTORE_API_KEY"
        )

    SINGLESTORE_API_KEY = value
    SINGLESTORE_DB_USERNAME = os.getenv("SINGLESTORE_DB_USERNAME", "")
    SINGLESTORE_DB_PASSWORD = os.getenv("SINGLESTORE_DB_PASSWORD", "")
