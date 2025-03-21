"""
Tool management functionality for Claude.
Provides a system for registering, managing, and executing tools with Claude,
including schema generation, callbacks, and execution handling.
"""
from typing import Dict, List, Optional, Callable, Any, Tuple, Union
import inspect
import json
from .schema import generate_tool_schema

class ToolManager:
    """
    Manages tool registration, schema generation, and execution.
    """
    
    def __init__(self, pre_callback: Optional[Callable] = None, post_callback: Optional[Callable] = None, text_callback: Optional[Callable] = None):
        """
        Initialize a tool manager.
        
        Args:
            pre_callback: Function to call before tool execution.
                          Must have signature (tool_name: str, tool_input: Dict[str, Any]) -> None
            post_callback: Function to call after tool execution.
                           Must have signature (tool_name: str, tool_input: Dict[str, Any], result: Any) -> Any
            text_callback: Function to call when a text block is received.
                           Must have signature (text: str) -> None
        """
        self.tools = {}
        self.text_editor_tool = None
        self.bash_tool = None
        
        # Initialize callbacks
        self.pre_tool_callback = None
        self.post_tool_callback = None
        self.text_callback = None
        
        # Check and set pre_callback if provided
        if pre_callback:
            sig = inspect.signature(pre_callback)
            params = list(sig.parameters.keys())
            if len(params) != 2:
                raise ValueError(f"Pre-tool callback must have exactly 2 parameters: (tool_func, tool_input). Got {len(params)} parameters: {params}")
            self.pre_tool_callback = pre_callback
        
        # Check and set post_callback if provided
        if post_callback:
            sig = inspect.signature(post_callback)
            params = list(sig.parameters.keys())
            if len(params) != 3:
                raise ValueError(f"Post-tool callback must have exactly 3 parameters: (tool_func, tool_input, result). Got {len(params)} parameters: {params}")
            self.post_tool_callback = post_callback
            
        # Check and set text_callback if provided
        if text_callback:
            sig = inspect.signature(text_callback)
            params = list(sig.parameters.keys())
            if len(params) != 1:
                raise ValueError(f"Text callback must have exactly 1 parameter: (text). Got {len(params)} parameters: {params}")
            if params[0] != "text":
                raise ValueError(f"Text callback must have a parameter named 'text'. Got: {params}")
            self.text_callback = text_callback
    
    def register_tools(self, tools: List[Callable]):
        """
        Register multiple tools.
        
        Args:
            tools: List of functions to register as tools
        """
        for tool in tools:
            # Get tool name (use function name if not provided)
            tool_name = tool.__name__
            
            # Store the function
            self.tools[tool_name] = tool
            
            # Check if this is a text editor tool or bash tool
            if tool_name == "str_replace_editor":
                self.text_editor_tool = tool
            elif tool_name == "bash":
                self.bash_tool = tool
    
    def get_tool_schemas(self) -> List[Dict]:
        """
        Get JSON schemas for all registered tools.
        
        Returns:
            List of tool schemas
        """
        schemas = []
        
        for name, func in self.tools.items():
            # Special handling for text editor tool and bash tool
            if name == "str_replace_editor" and self.text_editor_tool:
                # For text editor, only include name and type
                schemas.append({
                    "name": "str_replace_editor",
                    "type": "text_editor_20250124"
                })
            elif name == "bash" and self.bash_tool:
                # For bash tool, only include name and type
                schemas.append({
                    "name": "bash",
                    "type": "bash_20250124"
                })
            else:
                schema = generate_tool_schema(func, name)
                schemas.append(schema)
        
        return schemas
    
    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Union[str, Tuple[str, bool]]:
        """
        Execute a tool with the given input.
        
        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool
            
        Returns:
            Tool execution result as a string or a tuple of (content, is_error)
        """
        # Check if this is a text editor or bash tool request
        if tool_name == "str_replace_editor" and self.text_editor_tool:
            tool_func = self.text_editor_tool
        elif tool_name == "bash" and self.bash_tool:
            tool_func = self.bash_tool
        else:
            # Get the tool function
            tool_func = self.tools.get(tool_name)
        
        if not tool_func:
            return (f"Error: Tool '{tool_name}' not found", True)
        
        # Call pre-tool callback if available
        if self.pre_tool_callback:
            self.pre_tool_callback(tool_func, tool_input)
        
        # Execute the tool
        result = tool_func(**tool_input)
        
        # Call post-tool callback if available
        if self.post_tool_callback:
            result = self.post_tool_callback(tool_func, tool_input, result)
        
        # Handle tuple case for error reporting
        if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], bool):
            content, is_error = result
            # Convert content to string if it's not already
            if not isinstance(content, str):
                if isinstance(content, (dict, list)):
                    content = json.dumps(content)
                else:
                    content = str(content)
            return (content, is_error)
        
        # Convert result to string if it's not already
        if not isinstance(result, str):
            if isinstance(result, (dict, list)):
                result = json.dumps(result)
            else:
                result = str(result)
                
        return result