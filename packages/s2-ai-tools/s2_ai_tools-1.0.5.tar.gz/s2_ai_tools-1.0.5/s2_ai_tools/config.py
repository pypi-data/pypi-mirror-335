import os
from typing import Optional
from dotenv import load_dotenv

SINGLESTORE_API_BASE_URL = "https://api.singlestore.com"


def load_api_key() -> str:
    load_dotenv()
    api_key = os.getenv("SINGLESTORE_API_KEY")
    if not api_key:
        raise ValueError("SINGLESTORE_API_KEY environment variable is required")
    return api_key


def load_db_username() -> Optional[str]:
    load_dotenv()
    return os.getenv("SINGLESTORE_DB_USERNAME")


def load_db_password() -> Optional[str]:
    load_dotenv()
    return os.getenv("SINGLESTORE_DB_PASSWORD")
