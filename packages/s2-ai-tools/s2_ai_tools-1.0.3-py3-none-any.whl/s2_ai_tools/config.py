import os
from typing import Dict
from dotenv import load_dotenv


class Config:
    def __init__(self):
        load_dotenv()
        self.SINGLESTORE_API_KEY = os.getenv("SINGLESTORE_API_KEY")
        if not self.SINGLESTORE_API_KEY:
            raise EnvironmentError(
                "Missing required environment variable: SINGLESTORE_API_KEY"
            )
        self.SINGLESTORE_API_BASE_URL = "https://api.singlestore.com"
        self.SINGLESTORE_DB_USERNAME = os.getenv("SINGLESTORE_DB_USERNAME", "")
        self.SINGLESTORE_DB_PASSWORD = os.getenv("SINGLESTORE_DB_PASSWORD", "")
