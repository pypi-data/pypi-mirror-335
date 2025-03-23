from .definitions import tool_registry
from .config import (
    load_config,
)

# Initialize configuration
try:
    load_config()
except EnvironmentError as e:
    raise SystemExit(f"Singlestore ai tools configuration error: {e}")


class Tool:
    def __init__(self, name, description, func, inputSchema):
        self.name = name
        self.description = description
        self.func = func
        self.inputSchema = inputSchema


# Export the tools
tools_definitions = [
    Tool(
        name=tool["name"],
        description=tool["description"],
        func=tool["func"],
        inputSchema=tool["inputSchema"],
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
