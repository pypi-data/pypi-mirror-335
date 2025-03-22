from .definitions import tool_registry
from .config import (
    SINGLESTORE_API_KEY,
    SINGLESTORE_API_BASE_URL,
    SINGLESTORE_DB_USERNAME,
    SINGLESTORE_DB_PASSWORD,
    load_config,
)

# Initialize configuration
try:
    config = load_config()
    SINGLESTORE_API_KEY = config["SINGLESTORE_API_KEY"]
    SINGLESTORE_API_BASE_URL = config["SINGLESTORE_API_BASE_URL"]
    SINGLESTORE_DB_USERNAME = config.get("SINGLESTORE_DB_USERNAME")
    SINGLESTORE_DB_PASSWORD = config.get("SINGLESTORE_DB_PASSWORD")
except EnvironmentError as e:
    raise SystemExit(f"Singlestore ai tools configuration error: {e}")


class Tool:
    def __init__(self, name, description, func, input_schema):
        self.name = name
        self.description = description
        self.func = func
        self.input_schema = input_schema


# Export the tools
tools_definitions = [
    Tool(
        name=tool["name"],
        description=tool["description"],
        func=tool["func"],
    )
    for tool in tool_registry
]

# Create a dictionary for easy access to individual tools by name
tools_dict = {tool.name: tool for tool in tools_definitions}


# Export all tool names and config variables
__all__ = [
    "tools_definitions",
    "tools_dict",
]
