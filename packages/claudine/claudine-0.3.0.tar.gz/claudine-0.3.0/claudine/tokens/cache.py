"""
Token-related cache functionality.

This module provides tools for managing token caching,
including adding cache control markers to messages.
"""

from typing import Dict, List


def add_cache_control_to_messages(messages: List[Dict]) -> List[Dict]:
    """
    Process messages to add cache control attributes based on token count.
    
    Rules:
    - Add cache markers at minimum intervals of 1024 tokens
    - Maximum of 5 cache markers total
    - Only add cache markers to text content
    
    Args:
        messages: List of messages in the conversation
        
    Returns:
        Processed messages with cache control attributes
    """
    processed_messages = []
    markers_added = 0
    token_count_since_last_marker = 0
    
    for message_idx, message in enumerate(messages):
        # Create a copy of the message to avoid modifying the original
        processed_message = message.copy()
        
        # Process content if it's a list (structured content)
        if isinstance(message.get("content"), list):
            processed_content = []
            for content_idx, content_item in enumerate(message["content"]):
                # Only process text content items
                if isinstance(content_item, dict) and content_item.get("type") == "text":
                    # Estimate token count (rough approximation: 4 chars ≈ 1 token)
                    text = content_item.get("text", "")
                    estimated_tokens = len(text) // 4
                    token_count_since_last_marker += estimated_tokens
                    
                    # Add cache control if we've accumulated enough tokens and haven't exceeded max markers
                    if token_count_since_last_marker >= 1024 and markers_added < 5:
                        processed_item = content_item.copy()
                        processed_item["cache_control"] = {"type": "ephemeral"}
                        processed_content.append(processed_item)
                        markers_added += 1
                        token_count_since_last_marker = 0
                    else:
                        processed_content.append(content_item)
                else:
                    # Non-text content items are passed through unchanged
                    processed_content.append(content_item)
            
            processed_message["content"] = processed_content
        
        # Process string content (convert to structured content with cache control if needed)
        elif isinstance(message.get("content"), str) and message.get("content"):
            text_content = message["content"]
            estimated_tokens = len(text_content) // 4
            token_count_since_last_marker += estimated_tokens
            
            # Add cache control if we've accumulated enough tokens and haven't exceeded max markers
            if estimated_tokens >= 1024 and markers_added < 5:
                processed_message["content"] = [
                    {
                        "type": "text",
                        "text": text_content,
                        "cache_control": {"type": "ephemeral"}
                    }
                ]
                markers_added += 1
                token_count_since_last_marker = 0
        
        processed_messages.append(processed_message)
    
    return processed_messages


def estimate_token_count(text: str) -> int:
    """
    Estimate the number of tokens in a text string.
    
    This is a rough approximation based on character count.
    Claude tokenization is more complex, but this provides a reasonable estimate.
    
    Args:
        text: Text string to estimate tokens for
        
    Returns:
        Estimated number of tokens
    """
    # Rough approximation: 4 characters ≈ 1 token
    return len(text) // 4