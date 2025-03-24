"""
Example of implementing a simple bash tool that just prints the command and restart flag.
This demonstrates how to create a bash tool for use with the Claude agent.
"""
from typing import Optional, Tuple, Dict, Any
from claudine.agent import Agent

def simple_bash_tool(command: str, restart: Optional[bool] = False) -> Tuple[str, bool]:
    """
    A simple bash tool implementation that just prints the command and restart flag.
    
    Args:
        command: The bash command to execute
        restart: Whether to restart the process
        
    Returns:
        A tuple containing (output message, is_error flag)
    """
    # In a real implementation, this would execute the command
    # Here we just print what would be executed
    output = f"Would execute bash command: '{command}'\n"
    output += f"Restart flag is set to: {restart}"

    # Return the output with is_error=False
    return output, False

def main():
    # Create an agent with our simple bash tool
    agent = Agent(
        bash_tool=simple_bash_tool,
        system_prompt="You are a helpful assistant that can execute bash commands. When asked to perform file operations or system tasks, use the bash tool.",
        max_tokens=1024,
        verbose=True
    )

    # Start a conversation with the agent
    response = agent.query("list the files in the current dir")

    print("\nAgent response:")
    print(response)
    
    # Print token usage information
    token_usage = agent.get_tokens()
    print(f"\nToken usage:")
    print(f"Total input tokens: {token_usage.total_input}")
    print(f"Total output tokens: {token_usage.total_output}")


if __name__ == "__main__":
    main()