#!/usr/bin/env python3
from claudine import Agent
import sys

def main():
    """
    Example that demonstrates token usage and cost tracking with the Agent class.
    """
    # Initialize Agent
    agent = Agent(max_tokens=1000, config_params={"temperature": 0.7})
    
    # Make a simple API call
    prompt = "What is token counting in AI language models?"
    print(f"User: {prompt}")
    
    response = agent.query(prompt)
    
    # Print the response
    print(f"\nClaude's response:")
    print(response)
    
    # Get token usage information
    token_info = agent.get_tokens()
    
    # Print token usage information
    print("\nToken Usage Information:")
    print(f"Input tokens: {token_info.text_usage.input_tokens}")
    print(f"Output tokens: {token_info.text_usage.output_tokens}")
    print(f"Total tokens: {token_info.text_usage.total_tokens}")
    
    # Get cost information
    cost_info = agent.get_token_cost()
    
    print("\nCost Information:")
    print(f"Input cost: ${cost_info.input_cost:.4f}")
    print(f"Output cost: ${cost_info.output_cost:.4f}")
    print(f"Total cost: ${cost_info.total_cost:.4f}")
    
    # Make another API call
    second_prompt = "How can developers optimize token usage in their applications?"
    print(f"\nUser: {second_prompt}")
    
    second_response = agent.query(second_prompt)
    
    # Print the response
    print(f"\nClaude's response:")
    print(second_response)
    
    # Get updated token usage information
    token_info = agent.get_tokens()
    
    # Print updated token usage information
    print("\nUpdated Token Usage Information:")
    print(f"Total input tokens: {token_info.total_usage.input_tokens}")
    print(f"Total output tokens: {token_info.total_usage.output_tokens}")
    print(f"Total tokens: {token_info.total_usage.total_tokens}")
    
    # Get updated cost information
    cost_info = agent.get_token_cost()
    
    print("\nUpdated Cost Information:")
    print(f"Total cost: ${cost_info.total_cost:.4f}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
