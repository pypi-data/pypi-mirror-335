"""
Common utility functions for Claudine.
"""
from typing import Dict, List, Optional, Any, Union, Tuple
import uuid
import json

def generate_message_id() -> str:
    """
    Generate a unique message ID.
    
    Returns:
        Unique message ID
    """
    return f"msg_{uuid.uuid4().hex[:24]}"

def extract_text_content(content_blocks: List[Any]) -> str:
    """
    Extract text content from content blocks.
    
    Args:
        content_blocks: List of content blocks from Claude's response
        
    Returns:
        Concatenated text content
    """
    text_content = ""
    
    for block in content_blocks:
        if hasattr(block, 'type') and block.type == "text":
            text_content += block.text
    
    return text_content

def format_tool_result(tool_use_id: str, result: Union[str, Tuple[str, bool]]) -> Dict:
    """
    Format a tool result for sending to Claude.
    
    Args:
        tool_use_id: ID of the tool use
        result: Result of the tool execution, either a string or a tuple of (content, is_error)
        
    Returns:
        Formatted tool result
    """
    if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], bool):
        content, is_error = result
        return {
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "content": content,
            "is_error": is_error
        }
    else:
        return {
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "content": result
        }
