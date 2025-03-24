"""
Tool schema generation for Claude.
"""
from typing import Dict, List, Optional, Callable, Any, Tuple
import inspect
import json

def generate_tool_schema(func: Callable, name: Optional[str] = None) -> Dict:
    """
    Generate a JSON schema for a tool function.
    
    Args:
        func: Function to generate schema for
        name: Optional name for the tool (defaults to function name)
        
    Returns:
        Tool schema as a dictionary
    """
    # Get function signature
    sig = inspect.signature(func)
    
    # Get function name and docstring
    func_name = name if name else func.__name__
    func_desc = func.__doc__ or f"Function {func_name}"
    
    # Create parameter schema
    properties = {}
    required = []
    
    for param_name, param in sig.parameters.items():
        # Skip self parameter for methods
        if param_name == "self":
            continue
        
        # Add parameter to properties
        properties[param_name] = {
            "type": "string",  # Default to string type
            "description": f"Parameter {param_name}"
        }
        
        # Add to required list if no default value
        if param.default == inspect.Parameter.empty:
            required.append(param_name)
    
    # Create schema
    schema = {
        "name": func_name,
        "description": func_desc,
        "input_schema": {
            "type": "object",
            "properties": properties,
            "required": required
        }
    }
    
    return schema

def validate_tool_input(schema: Dict, input_data: Dict) -> Tuple[bool, Optional[str]]:
    """
    Validate tool input against its schema.
    
    Args:
        schema: Tool schema
        input_data: Input data to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Get required fields
    required = schema["input_schema"].get("required", [])
    
    # Check required fields
    for field in required:
        if field not in input_data:
            return False, f"Missing required field: {field}"
    
    # Validation passed
    return True, None
