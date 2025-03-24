from dataclasses import dataclass
from typing import Dict, Optional, Union

@dataclass
class TokenUsage:
    """Represents token usage information."""
    input_tokens: int = 0
    output_tokens: int = 0
    
    @property
    def total_tokens(self) -> int:
        """Calculate total tokens from input and output tokens"""
        return self.input_tokens + self.output_tokens

@dataclass
class TokenUsageInfo:
    """Comprehensive token usage information including text and tool usage."""
    text_usage: TokenUsage
    tools_usage: TokenUsage
    by_tool: Dict[str, TokenUsage] = None
    
    @property
    def total_usage(self) -> TokenUsage:
        """Get combined total usage across text and tools"""
        return TokenUsage(
            input_tokens=self.text_usage.input_tokens + self.tools_usage.input_tokens,
            output_tokens=self.text_usage.output_tokens + self.tools_usage.output_tokens
        )

class TokenTracker:
    """Tracks token usage for Claude API calls."""
    
    def __init__(self):
        """Initialize an empty token tracker."""
        self.messages = {}  # Dictionary to store message token usage by message ID
    
    def add_message(self, message_id: str, input_tokens: int, output_tokens: int, 
                   is_tool_related: bool = False, tool_name: Optional[str] = None,
                   parent_message_id: Optional[str] = None):
        """Add a message's token usage to the tracker."""
        self.messages[message_id] = {
            "message_id": message_id,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "is_tool_related": is_tool_related,
            "tool_name": tool_name,
            "parent_message_id": parent_message_id
        }
    
    def get_token_usage(self, message_id: Optional[str] = None) -> Union[Dict, TokenUsageInfo]:
        """Get token usage information for a specific message or consolidated usage."""
        if message_id:
            return self.messages.get(message_id, {})
        
        # Calculate total usage
        total_input = sum(msg["input_tokens"] for msg in self.messages.values())
        total_output = sum(msg["output_tokens"] for msg in self.messages.values())
        
        # Calculate tool-related usage
        tool_messages = [msg for msg in self.messages.values() if msg["is_tool_related"]]
        tool_input = sum(msg["input_tokens"] for msg in tool_messages)
        tool_output = sum(msg["output_tokens"] for msg in tool_messages)
        
        # Calculate text-only usage
        text_input = total_input - tool_input
        text_output = total_output - tool_output
        
        # Create TokenUsage objects
        text_usage = TokenUsage(
            input_tokens=text_input,
            output_tokens=text_output
        )
        
        tools_usage = TokenUsage(
            input_tokens=tool_input,
            output_tokens=tool_output
        )
        
        # Calculate usage by tool
        by_tool = {}
        for msg in self.messages.values():
            if msg["is_tool_related"] and msg["tool_name"]:
                tool_name = msg["tool_name"]
                
                if tool_name not in by_tool:
                    by_tool[tool_name] = {
                        "input_tokens": 0,
                        "output_tokens": 0
                    }
                
                by_tool[tool_name]["input_tokens"] += msg["input_tokens"]
                by_tool[tool_name]["output_tokens"] += msg["output_tokens"]
        
        # Convert by_tool to use TokenUsage objects
        by_tool_usage = {}
        for tool_name, usage in by_tool.items():
            by_tool_usage[tool_name] = TokenUsage(
                input_tokens=usage["input_tokens"],
                output_tokens=usage["output_tokens"]
            )
        
        return TokenUsageInfo(
            text_usage=text_usage,
            tools_usage=tools_usage,
            by_tool=by_tool_usage
        )

# Test the implementation
if __name__ == "__main__":
    # Create a token tracker and add some test messages
    tracker = TokenTracker()
    tracker.add_message('msg1', 100, 200, is_tool_related=False)
    tracker.add_message('msg2', 150, 250, is_tool_related=True, tool_name='calculator')
    tracker.add_message('msg3', 75, 125, is_tool_related=True, tool_name='weather')
    
    # Get the token usage information
    usage_info = tracker.get_token_usage()
    
    # Print the results
    print("=== Token Usage Test ===")
    print(f"Text usage: {usage_info.text_usage.input_tokens} input, {usage_info.text_usage.output_tokens} output, {usage_info.text_usage.total_tokens} total")
    print(f"Tools usage: {usage_info.tools_usage.input_tokens} input, {usage_info.tools_usage.output_tokens} output, {usage_info.tools_usage.total_tokens} total")
    print(f"Total usage: {usage_info.total_usage.input_tokens} input, {usage_info.total_usage.output_tokens} output, {usage_info.total_usage.total_tokens} total")
    
    print("\n=== By Tool ===")
    for tool_name, usage in usage_info.by_tool.items():
        print(f"Tool: {tool_name}")
        print(f"  Input tokens: {usage.input_tokens}")
        print(f"  Output tokens: {usage.output_tokens}")
        print(f"  Total tokens: {usage.total_tokens}")
