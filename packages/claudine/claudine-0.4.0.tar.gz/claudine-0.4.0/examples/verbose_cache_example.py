"""
Example demonstrating the verbose cache marker functionality.

This script shows how cache markers are added to messages and how
verbose mode prints information about these markers.
"""
import sys
import os
import time

# Add the parent directory to the path so we can import claudine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from claudine.agent import Agent
from claudine.tokens.cache import add_cache_control_to_messages

def main():
    # Check if verbose mode is enabled via command line argument
    verbose = "--verbose" in sys.argv
    
    # Create a long message that will trigger cache markers
    long_message = "This is a test message. " * 1000  # Approximately 5000 tokens
    
    print("Creating an agent with verbose mode...")
    agent = Agent(verbose=verbose)
    
    print("\nSending a long message to trigger cache markers...")
    response = agent.query(long_message)
    
    print("\nResponse received:")
    print(response[:200] + "..." if len(response) > 200 else response)
    
    # Display token usage information
    token_info = agent.get_tokens()
    print("\nToken usage information:")
    print(f"  Input tokens: {token_info.text_usage.input_tokens}")
    print(f"  Output tokens: {token_info.text_usage.output_tokens}")
    print(f"  Cache creation tokens: {token_info.text_usage.cache_creation_input_tokens}")
    print(f"  Cache read tokens: {token_info.text_usage.cache_read_input_tokens}")
    
    # Demonstrate the function directly
    if verbose:
        print("\nDemonstrating add_cache_control_to_messages function directly:")
        messages = [
            {"role": "user", "content": "This is a test message. " * 500}
        ]
        add_cache_control_to_messages(messages, verbose=True)

if __name__ == "__main__":
    main()