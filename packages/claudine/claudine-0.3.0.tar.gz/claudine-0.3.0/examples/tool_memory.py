#!/usr/bin/env python3
from claudine.agent import Agent
import sys
import os
from datetime import datetime
import random

def main():
    """
    Example that demonstrates how the agent maintains awareness of previous tool results
    and can reference them in subsequent responses.
    """
    
    # Define tool functions
    def generate_random_number(min_val=1, max_val=100):
        """Generates a random number between min_val and max_val."""
        number = random.randint(min_val, max_val)
        return f"Generated random number: {number}"
    
    def check_if_prime(number):
        """Checks if a number is prime."""
        try:
            num = int(number)
            if num < 2:
                return f"{num} is not a prime number."
            for i in range(2, int(num**0.5) + 1):
                if num % i == 0:
                    return f"{num} is not a prime number. It is divisible by {i}."
            return f"{num} is a prime number."
        except ValueError:
            return f"Error: '{number}' is not a valid integer."
    
    def get_current_time():
        """Returns the current date and time."""
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")
    
    # Define tools list
    tools = [generate_random_number, check_if_prime, get_current_time]
    
    # Define system prompt for the agent
    system_prompt = """
    You are a helpful AI assistant. Your primary goal is to assist the user with 
    information and general questions. When using tools, remember the results
    and be able to reference them in subsequent responses.
    """
    
    # Initialize Agent
    agent = Agent(system_prompt=system_prompt, tools=tools, verbose=True)
    
    # First prompt that uses a tool
    first_prompt = "Generate a random number for me."
    first_response = agent.query(first_prompt)
    
    print(f"User: {first_prompt}")
    print(f"Claude: {first_response}")
    
    # Second prompt that should reference the result of the first tool
    second_prompt = "Is the number you just generated a prime number?"
    second_response = agent.query(second_prompt)
    
    print(f"\nUser: {second_prompt}")
    print(f"Claude: {second_response}")
    
    # Third prompt to test memory of both previous tool results
    third_prompt = "What time is it now? And remind me what was the random number you generated and whether it was prime."
    third_response = agent.query(third_prompt)
    
    print(f"\nUser: {third_prompt}")
    print(f"Claude: {third_response}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
