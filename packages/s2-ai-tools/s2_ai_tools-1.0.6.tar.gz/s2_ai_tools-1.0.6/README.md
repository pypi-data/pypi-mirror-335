# Tool Definitions

This repository provides a comprehensive collection of SingleStore AI tools designed for seamless integration with LLM agents. These tools enable efficient database operations, query execution, and data management through natural language interactions.


## Installation

To install the tool definitions, run:

```bash
pip install s2_ai_tools
```

## Environment Setup

Create a `.env` file in your project root with the following variables:

```env
# SingleStore's management API key (required)
SINGLESTORE_API_KEY=your_api_key_here

# Database credentials (optional - can be provided as input parameters)
SINGLESTORE_DB_USERNAME=your_db_username_here
SINGLESTORE_DB_PASSWORD=your_db_password_here
```

These environment variables will be automatically loaded when the package is imported.

## Usage

Import the tool definitions in your project:

```python
from s2_ai_tools import tools_definitions, tool_dict
```

