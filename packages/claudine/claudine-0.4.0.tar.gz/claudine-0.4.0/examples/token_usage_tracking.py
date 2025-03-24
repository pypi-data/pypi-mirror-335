#!/usr/bin/env python3
from claudine import Agent
import sys

def main():
    """
    Example that demonstrates how to use the built-in token tracking and cost functionality.
    """
    # Initialize Agent
    agent = Agent(max_tokens=1000)
    
    # First prompt
    first_prompt = "Write a short poem about programming."
    first_response = agent.query(first_prompt)
    
    print(f"User: {first_prompt}")
    print(f"Claude: {first_response}")
    
    # Get token usage for the first message
    token_info = agent.get_tokens()
    
    print("\nToken Usage Information:")
    print(f"Input tokens: {token_info.text_usage.input_tokens}")
    print(f"Output tokens: {token_info.text_usage.output_tokens}")
    print(f"Total tokens: {token_info.text_usage.total_tokens}")
    print(f"Cache creation tokens: {token_info.text_usage.cache_creation_input_tokens}")
    print(f"Cache read tokens: {token_info.text_usage.cache_read_input_tokens}")
    
    # Get cost information
    cost_info = agent.get_token_cost()
    
    print("\nCost Information:")
    print(f"Input cost: {cost_info.format_input_cost()} {cost_info.unit}")
    print(f"Output cost: {cost_info.format_output_cost()} {cost_info.unit}")
    print(f"Cache creation cost: ${cost_info.cache_creation_cost:.6f} {cost_info.unit}")
    print(f"Cache read cost: ${cost_info.cache_read_cost:.6f} {cost_info.unit}")
    print(f"Total cost: {cost_info.format_total_cost()} {cost_info.unit}")
    
    # Second prompt
    second_prompt = "Explain how token counting works in large language models."
    second_response = agent.query(second_prompt)
    
    print(f"\nUser: {second_prompt}")
    print(f"Claude: {second_response}")
    
    # Get updated token usage
    token_info = agent.get_tokens()
    
    print("\nUpdated Token Usage:")
    print(f"Total input tokens: {token_info.total_usage.input_tokens}")
    print(f"Total output tokens: {token_info.total_usage.output_tokens}")
    print(f"Total tokens: {token_info.total_usage.total_tokens}")
    print(f"Total cache creation tokens: {token_info.total_usage.cache_creation_input_tokens}")
    print(f"Total cache read tokens: {token_info.total_usage.cache_read_input_tokens}")
    
    # Get updated cost information
    cost_info = agent.get_token_cost()
    
    print("\nUpdated Cost Information:")
    print(f"Input cost: {cost_info.format_input_cost()} {cost_info.unit}")
    print(f"Output cost: {cost_info.format_output_cost()} {cost_info.unit}")
    print(f"Cache creation cost: ${cost_info.cache_creation_cost:.6f} {cost_info.unit}")
    print(f"Cache read cost: ${cost_info.cache_read_cost:.6f} {cost_info.unit}")
    print(f"Total cost: {cost_info.format_total_cost()} {cost_info.unit}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
