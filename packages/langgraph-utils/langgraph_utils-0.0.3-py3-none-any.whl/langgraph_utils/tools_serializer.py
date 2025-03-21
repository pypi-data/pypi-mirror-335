from langchain_core.tools import StructuredTool
import json

"""
Converts a list of langchain tool objects into a JSON string.

:param tools: List of tool objects to be serialized.
:return: JSON string representation of the tools.
"""
def create_tools_json(tools):
    tools_json = []
    for tool in tools:
        tool_info = {
            'name': tool.name,
            'description': tool.description,
            'args_schema': tool.args_schema.model_json_schema()
        }
        tools_json.append(tool_info)
    return json.dumps(tools_json)



"""
Converts JSON formatted langchain tool into structured tool objects.
@param json_tools: A list or single JSON object representing tools.
@return: A list of StructuredTool objects or a single StructuredTool if only one is provided.
"""
def json_to_structured_tools(json_tools):
    if not isinstance(json_tools, list):
        json_tools = [json_tools]
    
    structured_tools = []
    for tool_json in json_tools:
            
        structured_tool = StructuredTool(
            name=tool_json['name'],
            description=tool_json['description'],
            func=None,
            args_schema=tool_json['args_schema']
        )
        structured_tools.append(structured_tool)
    
    return structured_tools if len(structured_tools) > 1 else structured_tools[0]