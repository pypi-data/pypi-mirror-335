"""
Message handling functionality for the Agent class.
"""
from typing import Dict, List, Optional, Union

from ..api.models import ToolUseResponse, TextResponse
from ..utils.helpers import extract_text_content


def extract_tool_info(messages: List[Dict]) -> tuple:
    """
    Extract tool-related information from messages.
    
    Args:
        messages: List of messages in the conversation
        
    Returns:
        Tuple of (is_tool_related, tool_name, parent_message_id)
    """
    is_tool_related = False
    tool_name = None
    parent_message_id = None
    
    # If this is a response to a tool result, it's tool-related
    if len(messages) >= 2 and isinstance(messages[-1].get("content"), list):
        for content_item in messages[-1].get("content", []):
            if isinstance(content_item, dict) and content_item.get("type") == "tool_result":
                is_tool_related = True
                # Try to find the parent message that initiated this tool call
                if len(messages) >= 3:
                    for content_item in messages[-2].get("content", []):
                        if isinstance(content_item, dict) and content_item.get("type") == "tool_use":
                            tool_name = content_item.get("name")
                            # Find the original message that triggered this tool
                            for i in range(len(messages) - 3, -1, -1):
                                if messages[i].get("role") == "assistant":
                                    parent_message_id = f"msg_{i}"  # Create a pseudo-ID
                                    break
    
    return is_tool_related, tool_name, parent_message_id


def process_response_content(response) -> str:
    """
    Process the response content and extract text.
    
    Args:
        response: Response from the API
        
    Returns:
        Extracted text content
    """
    text_content = ""
    for block in response.content:
        if block.type == "text" and block.text.strip():
            text_content += block.text
    
    return text_content


def filter_tool_messages(messages: List[Dict]) -> List[Dict]:
    """
    Filter out tool-related messages from the conversation.
    
    Args:
        messages: List of messages in the conversation
        
    Returns:
        Filtered list of messages
    """
    filtered_messages = []
    for message in messages:
        # Check if this is a tool-related message
        if isinstance(message.get("content"), list):
            is_tool_message = False
            for content_item in message["content"]:
                if isinstance(content_item, dict) and content_item.get("type") in ["tool_use", "tool_result"]:
                    is_tool_message = True
                    break
            
            if is_tool_message:
                continue
        
        filtered_messages.append(message)
    
    return filtered_messages
