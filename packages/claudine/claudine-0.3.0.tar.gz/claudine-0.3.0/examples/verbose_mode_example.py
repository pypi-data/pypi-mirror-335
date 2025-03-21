#!/usr/bin/env python3
"""
Example demonstrating the verbose parameter for the Claudine Agent.
This shows how to enable verbose mode and what kind of information it provides.
"""
from claudine import Agent
import sys

def main():
    """
    Demonstrates how to use the verbose parameter for the Claudine Agent.
    """
    # Check if verbose mode is enabled via command line argument
    verbose = "--verbose" in sys.argv
    
    # Initialize Agent with verbose mode based on argument
    # Using the new config_params approach
    agent = Agent(
        config_params={
            "temperature": 0.7,
            "top_p": 0.95
        }, 
        verbose=verbose
    )
    
    # Alternatively, you could use the backward-compatible approach:
    # agent = Agent(config_params={"temperature": 0.7}, verbose=verbose)
    
    if verbose:
        print("Verbose mode enabled - API calls and token tracking details will be shown")
    else:
        print("Verbose mode disabled - run with --verbose to see detailed information")
    
    # Process a simple prompt
    prompt = "Explain what token tracking is in 2-3 sentences."
    print(f"\nSending prompt: '{prompt}'")
    
    response = agent.query(prompt)
    print(f"\nClaude's response: {response}")
    
    # Get token usage
    token_info = agent.get_tokens()
    print("\nToken Usage Summary:")
    print(f"Input tokens: {token_info.total_usage.input_tokens}")
    print(f"Output tokens: {token_info.total_usage.output_tokens}")
    
    # Get cost information
    cost_info = agent.get_token_cost()
    print(f"Total cost: ${cost_info.total_cost:.6f}")

if __name__ == "__main__":
    main()
