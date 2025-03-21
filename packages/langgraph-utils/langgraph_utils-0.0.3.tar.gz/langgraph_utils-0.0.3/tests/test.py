from langgraph_utils import create_tools_json, json_to_structured_tools
from langchain_core.tools import tool

# @! create simple tool to add two numbers and genberate random hash from passed string 

import hashlib
import random

from langchain_core.tools import tool

@tool
def add_numbers(num1, num2):
    """
    This function adds two numbers.

    Parameters:
    num1 (int): The first number to add.
    num2 (int): The second number to add.

    Returns:
    The sum of num1 and num2.
    """
    return num1 + num2

@tool
def generate_hash(input_string):
    """
    This function generates a unique hash for a given input string.

    Parameters:
    input_string (str): The string for which the hash is to be generated.

    Returns:
    str: The generated hash of the input string.
    """
    random.seed(input_string)
    return hashlib.sha256(str(random.random()).encode()).hexdigest()

tools = [add_numbers, generate_hash]
json_tools = create_tools_json(tools)
import json
tools_from_json = json_to_structured_tools(json_tools)
print(json.dumps(json_tools))