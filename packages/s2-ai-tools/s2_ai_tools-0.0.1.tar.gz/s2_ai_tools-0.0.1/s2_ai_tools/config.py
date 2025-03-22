import os
from typing import Dict
from dotenv import load_dotenv

SINGLESTORE_API_KEY = ""
SINGLESTORE_API_BASE_URL = "https://api.singlestore.com"
SINGLESTORE_DB_USERNAME = ""
SINGLESTORE_DB_PASSWORD = ""


def load_config() -> Dict[str, str]:
    """Load and validate environment variables."""
    load_dotenv()  # Loads environment variables from a .env file

    # Only API key is required
    required_vars = ["SINGLESTORE_API_KEY"]
    # Optional database credentials
    optional_vars = ["SINGLESTORE_DB_USERNAME", "SINGLESTORE_DB_PASSWORD"]

    config = {}
    missing_vars = []

    # Check required vars
    for var in required_vars:
        value = os.getenv(var)
        if value is None or value.strip() == "":
            missing_vars.append(var)
        else:
            config[var] = value

    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

    # Add optional vars if they exist
    for var in optional_vars:
        value = os.getenv(var)
        if value and value.strip():
            config[var] = value

    return config
