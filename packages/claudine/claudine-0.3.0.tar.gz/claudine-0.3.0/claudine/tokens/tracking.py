"""
Token tracking functionality for Claude API.

This module provides tools for tracking token usage across
conversations, including separate tracking for text and tool interactions.
"""

from typing import Dict, Optional, Union, Tuple
from .models import TokenUsage, TokenUsageInfo, TokenCost
from .pricing import MODEL_PRICING, DEFAULT_MODEL, get_model_pricing

class TokenManager:
    """
    Manages token usage, costs, and file operations for Claude API calls.
    """
    
    def __init__(self, model: str = DEFAULT_MODEL, verbose: bool = False):
        """
        Initialize an empty token manager.
        
        Args:
            model: Model identifier to use for pricing calculations
            verbose: If True, print detailed information about token usage
        """
        self.messages = {}  # Dictionary to store message token usage by message ID
        self.model = model
        self.verbose = verbose
    
    def add_message(self, message_id: str, usage, 
                   is_tool_related: bool = False, tool_name: Optional[str] = None,
                   parent_message_id: Optional[str] = None):
        """
        Add a message's token usage to the manager.
        
        Args:
            message_id: Unique ID of the message
            usage: Usage object containing token metrics
            is_tool_related: Whether this message is part of a tool call sequence
            tool_name: Name of the tool if is_tool_related is True
            parent_message_id: ID of the parent message that initiated the tool call
            
        Raises:
            AttributeError: If required token metrics are not found in the usage object
        """
        # Access token metrics directly - will raise AttributeError if not present
        input_tokens = usage.input_tokens
        output_tokens = usage.output_tokens
        cache_creation_input_tokens = usage.cache_creation_input_tokens
        cache_read_input_tokens = usage.cache_read_input_tokens
        
        self.messages[message_id] = {
            "message_id": message_id,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cache_creation_input_tokens": cache_creation_input_tokens,
            "cache_read_input_tokens": cache_read_input_tokens,
            "is_tool_related": is_tool_related,
            "tool_name": tool_name,
            "parent_message_id": parent_message_id
        }
        
        # Print debug information if verbose mode is enabled
        if self.verbose:
            message_type = f"Tool ({tool_name})" if is_tool_related else "Text"
            print(f"\n[DEBUG] Token Tracking - Message: {message_id[:8]}...")
            print(f"  Type: {message_type}")
            print(f"  Input tokens: {input_tokens}")
            print(f"  Output tokens: {output_tokens}")
            print(f"  Cache creation tokens: {cache_creation_input_tokens}")
            print(f"  Cache read tokens: {cache_read_input_tokens}")
            if parent_message_id:
                print(f"  Parent message: {parent_message_id[:8]}...")
    
    def get_token_usage(self, message_id: Optional[str] = None) -> Union[Dict, TokenUsageInfo]:
        """
        Get token usage information for a specific message or consolidated usage.
        
        Args:
            message_id: Optional ID of the message to get token usage for.
                        If None, returns consolidated token usage information.
        
        Returns:
            If message_id is provided: Token usage information for that message
            If message_id is None: TokenUsageInfo with text and tool usage information
        """
        if message_id:
            return self.messages.get(message_id, {})
        
        # Calculate total usage
        total_input = sum(msg["input_tokens"] for msg in self.messages.values())
        total_output = sum(msg["output_tokens"] for msg in self.messages.values())
        total_cache_creation = sum(msg["cache_creation_input_tokens"] for msg in self.messages.values())
        total_cache_read = sum(msg["cache_read_input_tokens"] for msg in self.messages.values())
        
        # Calculate tool-related usage
        tool_messages = [msg for msg in self.messages.values() if msg["is_tool_related"]]
        tool_input = sum(msg["input_tokens"] for msg in tool_messages)
        tool_output = sum(msg["output_tokens"] for msg in tool_messages)
        tool_cache_creation = sum(msg["cache_creation_input_tokens"] for msg in tool_messages)
        tool_cache_read = sum(msg["cache_read_input_tokens"] for msg in tool_messages)
        
        # Calculate text-only usage
        text_input = total_input - tool_input
        text_output = total_output - tool_output
        text_cache_creation = total_cache_creation - tool_cache_creation
        text_cache_read = total_cache_read - tool_cache_read
        
        # Create TokenUsage objects
        text_usage = TokenUsage(
            input_tokens=text_input,
            output_tokens=text_output,
            cache_creation_input_tokens=text_cache_creation,
            cache_read_input_tokens=text_cache_read
        )
        
        tools_usage = TokenUsage(
            input_tokens=tool_input,
            output_tokens=tool_output,
            cache_creation_input_tokens=tool_cache_creation,
            cache_read_input_tokens=tool_cache_read
        )
        
        # Calculate usage by tool
        by_tool = {}
        for msg in self.messages.values():
            if msg["is_tool_related"] and msg["tool_name"]:
                tool_name = msg["tool_name"]
                
                if tool_name not in by_tool:
                    by_tool[tool_name] = {
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "cache_creation_input_tokens": 0,
                        "cache_read_input_tokens": 0
                    }
                
                by_tool[tool_name]["input_tokens"] += msg["input_tokens"]
                by_tool[tool_name]["output_tokens"] += msg["output_tokens"]
                by_tool[tool_name]["cache_creation_input_tokens"] += msg["cache_creation_input_tokens"]
                by_tool[tool_name]["cache_read_input_tokens"] += msg["cache_read_input_tokens"]
        
        # Convert by_tool to use TokenUsage objects
        by_tool_usage = {}
        for tool_name, usage in by_tool.items():
            by_tool_usage[tool_name] = TokenUsage(
                input_tokens=usage["input_tokens"],
                output_tokens=usage["output_tokens"],
                cache_creation_input_tokens=usage["cache_creation_input_tokens"],
                cache_read_input_tokens=usage["cache_read_input_tokens"]
            )
        
        return TokenUsageInfo(
            text_usage=text_usage,
            tools_usage=tools_usage,
            by_tool=by_tool_usage
        )
    
    def get_cost(self, message_id: Optional[str] = None) -> TokenCost:
        """
        Get cost information for token usage.
        
        Args:
            message_id: Optional ID of the message to get cost for.
                        If None, returns consolidated cost information.
                        
        Returns:
            TokenCost object with cost information
        """
        if not self.model:
            return TokenCost()
        
        pricing = get_model_pricing(self.model)
        if not pricing:
            return TokenCost(
                input_cost=0.0,
                output_cost=0.0,
                cache_creation_cost=0.0,
                cache_read_cost=0.0,
                unit="USD"
            )
        
        # If it's a single message, calculate cost for that message
        if message_id and message_id in self.messages:
            usage = self.messages[message_id]
            token_usage = TokenUsage(
                input_tokens=usage.get("input_tokens", 0),
                output_tokens=usage.get("output_tokens", 0),
                cache_creation_input_tokens=usage.get("cache_creation_input_tokens", 0),
                cache_read_input_tokens=usage.get("cache_read_input_tokens", 0)
            )
            cost_dict = token_usage.calculate_cost(pricing)
            
            # Calculate cache delta (savings from using cache)
            standard_cost = pricing.input_tokens.calculate_cost(
                token_usage.input_tokens + 
                token_usage.cache_creation_input_tokens + 
                token_usage.cache_read_input_tokens
            )
            actual_cost = cost_dict["input_cost"] + cost_dict["cache_creation_cost"] + cost_dict["cache_read_cost"]
            cache_delta = standard_cost - actual_cost
            
            return TokenCost(
                input_cost=cost_dict["input_cost"],
                output_cost=cost_dict["output_cost"],
                cache_creation_cost=cost_dict["cache_creation_cost"],
                cache_read_cost=cost_dict["cache_read_cost"],
                cache_delta=cache_delta,
                unit=pricing.input_tokens.unit
            )
        
        # For consolidated usage, extract the total cost from the cost dictionary
        usage = self.get_token_usage()
        cost_dict = usage.total_usage.calculate_cost(pricing)
        
        # Calculate cache delta (savings from using cache)
        total_usage = usage.total_usage
        standard_cost = pricing.input_tokens.calculate_cost(
            total_usage.input_tokens + 
            total_usage.cache_creation_input_tokens + 
            total_usage.cache_read_input_tokens
        )
        actual_cost = cost_dict["input_cost"] + cost_dict["cache_creation_cost"] + cost_dict["cache_read_cost"]
        cache_delta = standard_cost - actual_cost
        
        return TokenCost(
            input_cost=cost_dict["input_cost"],
            output_cost=cost_dict["output_cost"],
            cache_creation_cost=cost_dict["cache_creation_cost"],
            cache_read_cost=cost_dict["cache_read_cost"],
            cache_delta=cache_delta,
            unit=pricing.input_tokens.unit
        )
    

    
    def reset(self):
        """Reset all token usage data."""
        self.messages = {}