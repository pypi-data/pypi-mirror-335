from langchain_core.tools import StructuredTool

def create_tools_json(tools):
    tools_json = []
    for tool in tools:
        tool_info = {
            'name': tool.name,
            'description': tool.description,
            'args_schema': tool.args_schema.model_json_schema()
        }
        tools_json.append(tool_info)
    return tools_json

# @! create function to convert json_output to structuredtool or list of structuredtool basis input type provider=anthropic

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