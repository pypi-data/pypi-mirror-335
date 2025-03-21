"""
Example showing the sequence of callbacks during a conversation with multiple tool calls.
"""
import os
from typing import Dict, Any, Callable
from datetime import datetime

from claudine import Agent

# Callback counters
text_callbacks = 0
pre_tool_callbacks = 0
post_tool_callbacks = 0
text_blocks = []

# Define tools
def get_time():
    """Get the current time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_weather(location: str):
    """Get the weather for a location."""
    # This is a mock implementation
    return f"72°F and sunny in {location}"

def calculate(expression: str):
    """Calculate the result of a mathematical expression."""
    try:
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"

# Define callbacks
def text_callback(text: str):
    """Callback for text responses."""
    global text_callbacks
    text_callbacks += 1
    # Store the text block with its index
    text_blocks.append(f"TEXT BLOCK #{text_callbacks}: {text[:100]}{'...' if len(text) > 100 else ''}")
    print(f"\n[TEXT #{text_callbacks}] Received text: {text[:100]}{'...' if len(text) > 100 else ''}")
    print(f"[TEXT] Text length: {len(text)}")

def pre_tool_callback(tool_func: Callable, tool_input: Dict[str, Any]):
    """Callback before tool execution."""
    global pre_tool_callbacks
    pre_tool_callbacks += 1
    tool_name = tool_func.__name__
    print(f"\n[PRE-TOOL #{pre_tool_callbacks}] About to execute: {tool_name}")
    print(f"[PRE-TOOL] Input parameters: {tool_input}")

def post_tool_callback(tool_func: Callable, tool_input: Dict[str, Any], result: Any):
    """Callback after tool execution."""
    global post_tool_callbacks
    post_tool_callbacks += 1
    tool_name = tool_func.__name__
    print(f"[POST-TOOL #{post_tool_callbacks}] Tool executed: {tool_name}")
    print(f"[POST-TOOL] Result: {result}")
    return result

def main():
    """Run the example."""
    # Get API key from environment variable
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Please set the ANTHROPIC_API_KEY environment variable.")
        return
    
    # Create agent with tools and callbacks
    agent = Agent(
        api_key=api_key,
        tools=[get_time, get_weather, calculate],
        callbacks={
            "text": text_callback,
            "pre_tool": pre_tool_callback,
            "post_tool": post_tool_callback
        },
        # Enable verbose mode to see all API requests and responses
        verbose=True
    )
    
    # Print header
    print("=" * 80)
    print("EXAMPLE: Multiple tool calls and final answer")
    print("=" * 80)
    print()
    
    # Process prompt
    prompt = "What time is it now, and what's the weather in San Francisco? Also, calculate 25 * 18.   "
    print(f"User: {prompt}\n")
    response = agent.query(prompt)
    
    # Print final response
    print("\n" + "=" * 80)
    print("FINAL RESPONSE:")
    print("=" * 80)
    print(f"Claude: {response}")
    
    # Print callback counts
    print("\n" + "=" * 80)
    print("CALLBACK COUNTS:")
    print("=" * 80)
    print(f"Text callbacks: {text_callbacks}")
    print(f"Pre-tool callbacks: {pre_tool_callbacks}")
    print(f"Post-tool callbacks: {post_tool_callbacks}")
    
    # Print all text blocks received
    print("\n" + "=" * 80)
    print("TEXT BLOCKS RECEIVED:")
    print("=" * 80)
    for block in text_blocks:
        print(block)
    
    # Print token usage
    print("\n" + "=" * 80)
    print("TOKEN USAGE:")
    print("=" * 80)
    token_usage = agent.get_tokens()
    print(f"Text Usage:")
    print(f"  Input tokens: {token_usage.text_usage.input_tokens}")
    print(f"  Output tokens: {token_usage.text_usage.output_tokens}")
    print(f"  Total tokens: {token_usage.text_usage.total_tokens}")
    print()
    print(f"Tools Usage:")
    print(f"  Input tokens: {token_usage.tools_usage.input_tokens}")
    print(f"  Output tokens: {token_usage.tools_usage.output_tokens}")
    print(f"  Total tokens: {token_usage.tools_usage.total_tokens}")
    print()
    print(f"Total Usage:")
    print(f"  Input tokens: {token_usage.total_usage.input_tokens}")
    print(f"  Output tokens: {token_usage.total_usage.output_tokens}")
    print(f"  Total tokens: {token_usage.total_usage.total_tokens}")
    print()
    print(f"Usage by Tool:")
    if token_usage.by_tool:
        for tool_name, usage in token_usage.by_tool.items():
            print(f"  {tool_name}:")
            print(f"    Input tokens: {usage.input_tokens}")
            print(f"    Output tokens: {usage.output_tokens}")
            print(f"    Total tokens: {usage.total_tokens}")
    
    # Print cost information
    print("\n" + "=" * 80)
    print("COST INFORMATION:")
    print("=" * 80)
    cost = agent.get_token_cost()
    print(f"Input cost: {cost.format_input_cost()}")
    print(f"Output cost: {cost.format_output_cost()}")
    print(f"Total cost: {cost.format_total_cost()}")

if __name__ == "__main__":
    main()
