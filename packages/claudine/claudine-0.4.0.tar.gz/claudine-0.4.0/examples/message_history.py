#!/usr/bin/env python3
from claudine import Agent
import sys
import os

def main():
    """
    Example that demonstrates how the agent maintains message history
    and can reference previous answers in subsequent responses.
    """
    # Check for API key
    if "ANTHROPIC_API_KEY" not in os.environ:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set your Anthropic API key with:")
        print("  export ANTHROPIC_API_KEY=your_api_key_here (Linux/Mac)")
        print("  set ANTHROPIC_API_KEY=your_api_key_here (Windows)")
        return 1
    
    # Define instructions for the agent
    instructions = """
    You are a helpful AI assistant. Your primary goal is to assist the user with 
    information and general questions. When the user asks follow-up questions,
    you should remember and reference your previous answers.
    """
    
    # Initialize Agent
    agent = Agent(instructions=instructions)
    
    # First question
    first_prompt = "Generate a random 4-digit number for me to use as a PIN code."
    first_response = agent.query(first_prompt)
    
    print(f"User: {first_prompt}")
    print(f"Claude: {first_response}")
    
    # Second question that references the first answer
    second_prompt = "What was the PIN code you just gave me? Also, tell me what would happen if I added 1 to that number."
    second_response = agent.query(second_prompt)
    
    print(f"\nUser: {second_prompt}")
    print(f"Claude: {second_response}")
    
    # Third question to further test memory
    third_prompt = "Can you remind me what the original PIN was and what number you calculated when adding 1 to it?"
    third_response = agent.query(third_prompt)
    
    print(f"\nUser: {third_prompt}")
    print(f"Claude: {third_response}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
