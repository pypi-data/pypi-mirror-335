#!/usr/bin/env python3
from claudine import Agent
import sys
import json

def weather_tool(location: str, unit: str = "celsius"):
    """
    Get the current weather for a location.
    
    Args:
        location: The location to get weather for
        unit: Temperature unit (celsius or fahrenheit)
        
    Returns:
        Weather information as a string
    """
    # This is a mock implementation
    weather_data = {
        "location": location,
        "temperature": 22 if unit == "celsius" else 72,
        "conditions": "Sunny",
        "humidity": "45%"
    }
    
    return json.dumps(weather_data)

def calculator(expression: str):
    """
    Calculate the result of a mathematical expression.
    
    Args:
        expression: Mathematical expression to evaluate
        
    Returns:
        Result of the calculation
    """
    try:
        # Warning: eval can be dangerous in production code
        # This is just for demonstration purposes
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    """
    Example that demonstrates token usage tracking with tools.
    """
    
    # Initialize Agent with tools
    agent = Agent(
        max_tokens=1000, 
        config_params={"temperature": 0.7},
        tools=[weather_tool, calculator]
    )
    
    # Process a prompt that will likely use tools
    response = agent.query(
        "What's the weather in New York? Also, what is 1234 * 5678?"
    )
    
    # Print the response
    print("Claude's response:")
    print(response)
    print("\n" + "-" * 50 + "\n")
    
    # Get token usage information
    token_info = agent.get_tokens()
    
    print("Token Usage Information:")
    print(f"Text input tokens: {token_info.text_usage.input_tokens}")
    print(f"Text output tokens: {token_info.text_usage.output_tokens}")
    print(f"Text total tokens: {token_info.text_usage.total_tokens}")
    print(f"Tool input tokens: {token_info.tools_usage.input_tokens}")
    print(f"Tool output tokens: {token_info.tools_usage.output_tokens}")
    print(f"Tool total tokens: {token_info.tools_usage.total_tokens}")
    
    # Print total token usage
    print("\n" + "-" * 50 + "\n")
    print("Total Token Usage:")
    total = token_info.total_usage
    print(f"Total input tokens: {total.input_tokens}")
    print(f"Total output tokens: {total.output_tokens}")
    print(f"Total tokens: {total.total_tokens}")
    
    # Get cost information
    cost_info = agent.get_token_cost()
    
    print("\n" + "-" * 50 + "\n")
    print("Cost Information:")
    print(f"Input cost: {cost_info.format_input_cost()} {cost_info.unit}")
    print(f"Output cost: {cost_info.format_output_cost()} {cost_info.unit}")
    print(f"Total cost: {cost_info.format_total_cost()} {cost_info.unit}")
    
    # Print token usage by tool
    print("\n" + "-" * 50 + "\n")
    print("Token Usage by Tool:")
    for tool_name, usage in token_info.by_tool.items():
        print(f"\nTool: {tool_name}")
        print(f"  Input tokens: {usage.input_tokens}")
        print(f"  Output tokens: {usage.output_tokens}")
        print(f"  Total tokens: {usage.total_tokens}")
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
