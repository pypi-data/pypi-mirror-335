#!/usr/bin/env python3
from claudine.agent import Agent
import sys

def main():
    """
    Example that demonstrates how to obtain token usage and cost information
    after making calls to the Claudine Agent.
    """
    
    # Initialize Agent with config_params
    agent = Agent(
        max_tokens=1000, 
        config_params={
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 50
        },
        verbose=True
    )
    
    # Simple message to the API
    response = agent.query("Write a short poem about programming.")
    
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
    print(f"Text cache creation input tokens: {token_info.text_usage.cache_creation_input_tokens}")
    print(f"Text cache read input tokens: {token_info.text_usage.cache_read_input_tokens}")
    print(f"Tool input tokens: {token_info.tools_usage.input_tokens}")
    print(f"Tool output tokens: {token_info.tools_usage.output_tokens}")
    print(f"Tool total tokens: {token_info.tools_usage.total_tokens}")
    print(f"Tool cache creation input tokens: {token_info.tools_usage.cache_creation_input_tokens}")
    print(f"Tool cache read input tokens: {token_info.tools_usage.cache_read_input_tokens}")
    print(f"Total input tokens: {token_info.total_usage.input_tokens}")
    print(f"Total output tokens: {token_info.total_usage.output_tokens}")
    print(f"Total tokens: {token_info.total_usage.total_tokens}")
    print(f"Total cache creation input tokens: {token_info.total_usage.cache_creation_input_tokens}")
    print(f"Total cache read input tokens: {token_info.total_usage.cache_read_input_tokens}")
    
    # Get cost information
    cost_info = agent.get_token_cost()
    
    print("\nCost Information:")
    print(f"Input cost: {cost_info.format_input_cost()} {cost_info.unit}")
    print(f"Output cost: {cost_info.format_output_cost()} {cost_info.unit}")
    print(f"Total cost: {cost_info.format_total_cost()} {cost_info.unit}")
    
    # Example with a longer prompt
    print("\n" + "-" * 50 + "\n")
    print("Example with a longer prompt:")
    
    longer_response = agent.query("Explain how token counting works in large language models and why it matters for API usage.")
    
    # Print the response
    print("Claude's response:")
    print(longer_response)
    print("\n" + "-" * 50 + "\n")
    
    # Get updated token usage information
    token_info = agent.get_tokens()
    
    print("Updated Token Usage Information:")
    print(f"Total input tokens: {token_info.total_usage.input_tokens}")
    print(f"Total output tokens: {token_info.total_usage.output_tokens}")
    print(f"Total tokens: {token_info.total_usage.total_tokens}")
    print(f"Total cache creation input tokens: {token_info.total_usage.cache_creation_input_tokens}")
    print(f"Total cache read input tokens: {token_info.total_usage.cache_read_input_tokens}")
    
    # Get updated cost information
    cost_info = agent.get_token_cost()
    
    print("\nUpdated Cost Information:")
    print(f"Total cost: {cost_info.format_total_cost()} {cost_info.unit}")
    
    # Example with repeated prompt to demonstrate caching
    print("\n" + "-" * 50 + "\n")
    print("Example with repeated prompt to demonstrate caching:")
    
    # Reset the agent to ensure a clean state
    agent.reset()
    
    # First call - should create cache
    print("\nFirst call (cache creation):")
    cached_prompt = "What is the capital of France?"
    cached_response = agent.query(cached_prompt)
    print(f"Claude's response: {cached_response}")
    
    # Get token usage after first call
    token_info = agent.get_tokens()
    print("\nToken Usage After First Call:")
    print(f"Input tokens: {token_info.total_usage.input_tokens}")
    print(f"Output tokens: {token_info.total_usage.output_tokens}")
    print(f"Cache creation input tokens: {token_info.total_usage.cache_creation_input_tokens}")
    print(f"Cache read input tokens: {token_info.total_usage.cache_read_input_tokens}")
    
    # Second call - should use cache
    print("\nSecond call (cache read):")
    cached_response = agent.query(cached_prompt)
    print(f"Claude's response: {cached_response}")
    
    # Get token usage after second call
    token_info = agent.get_tokens()
    print("\nToken Usage After Second Call:")
    print(f"Input tokens: {token_info.total_usage.input_tokens}")
    print(f"Output tokens: {token_info.total_usage.output_tokens}")
    print(f"Cache creation input tokens: {token_info.total_usage.cache_creation_input_tokens}")
    print(f"Cache read input tokens: {token_info.total_usage.cache_read_input_tokens}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
