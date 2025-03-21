# LangChain Tools JSON Converter

This module provides utility functions to convert LangChain tool objects into JSON format and vice versa. It helps serialize and deserialize structured tool definitions for easier storage and transport.

## Features
- **`create_tools_json`**: Converts a list of LangChain tool objects into a JSON string.
- **`json_to_structured_tools`**: Converts a JSON representation of LangChain tools back into `StructuredTool` objects.

## Installation
Ensure you have `langchain_core` installed before using this module:
```bash
pip install langchain-core
```

## Usage
### Converting Tools to JSON
```python
from langchain_core.tools import StructuredTool

# Example tool
example_tool = StructuredTool(
    name="example_tool",
    description="An example tool",
    func=None,
    args_schema={}
)

# Convert to JSON
json_output = create_tools_json([example_tool])
print(json_output)
```

### Converting JSON to Structured Tools
```python
json_tools = [
    {
        "name": "example_tool",
        "description": "An example tool",
        "args_schema": {}
    }
]

structured_tools = json_to_structured_tools(json_tools)
print(structured_tools)
```

## Function Details
### `create_tools_json(tools)`
**Description:** Converts a list of LangChain tool objects into a JSON string.

**Parameters:**
- `tools` (List of `StructuredTool` objects): List of tool objects to be serialized.

**Returns:**
- `str`: JSON string representation of the tools.

### `json_to_structured_tools(json_tools)`
**Description:** Converts JSON-formatted LangChain tools into `StructuredTool` objects.

**Parameters:**
- `json_tools` (list or dict): A list or single JSON object representing tools.

**Returns:**
- `StructuredTool` or List of `StructuredTool` objects.

## Notes
- The `func` attribute is set to `None` when reconstructing `StructuredTool` objects from JSON.
- Ensure that the `args_schema` matches the expected schema format for LangChain.

## License
This module is open-source and can be modified as needed.

