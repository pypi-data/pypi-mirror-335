"""
Example demonstrating the callback signature validation.
"""
from claudine import Agent, create_logging_callbacks

def main():
    # Define our own callbacks with the correct signatures
    def pre_tool_callback(tool_func, tool_input):
        tool_name = tool_func.__name__
        print(f" About to execute: {tool_name}")
        print(f" Input parameters: {tool_input}")
    
    def post_tool_callback(tool_func, tool_input, result):
        tool_name = tool_func.__name__
        print(f" Tool executed successfully: {tool_name}")
        print(f" Result: {result}")
        return result
    
    def text_callback(text):
        print(f" Received text: {text}")
    
    # Set up the callbacks dictionary
    callbacks = {
        "pre_tool": pre_tool_callback,
        "post_tool": post_tool_callback,
        "text": text_callback
    }
    
    # This will work fine
    agent = Agent(
        api_key="your_api_key",
        callbacks=callbacks
    )
    print("Successfully set up agent with valid callbacks")
    
    # Invalid pre-callback (wrong number of parameters)
    def invalid_pre_callback(tool_func):
        print(f"Invalid pre-callback called for: {tool_func.__name__}")
    
    try:
        agent = Agent(
            api_key="your_api_key",
            callbacks={"pre_tool": invalid_pre_callback, "post_tool": callbacks["post_tool"], "text": callbacks["text"]}
        )
        print("This should not be printed")
    except ValueError as e:
        print(f"Caught expected error: {e}")
    
    # Invalid post-callback (wrong number of parameters)
    def invalid_post_callback(tool_func, tool_input):
        print(f"Invalid post-callback called for: {tool_func.__name__}")
        return "Modified result"
    
    try:
        agent = Agent(
            api_key="your_api_key",
            callbacks={"pre_tool": callbacks["pre_tool"], "post_tool": invalid_post_callback, "text": callbacks["text"]}
        )
        print("This should not be printed")
    except ValueError as e:
        print(f"Caught expected error: {e}")
    
    # Invalid text callback (wrong number of parameters)
    def invalid_text_callback(text, extra_param):
        print(f"Invalid text callback called with: {text}")
    
    try:
        agent = Agent(
            api_key="your_api_key",
            callbacks={"pre_tool": callbacks["pre_tool"], "post_tool": callbacks["post_tool"], "text": invalid_text_callback}
        )
        print("This should not be printed")
    except ValueError as e:
        print(f"Caught expected error: {e}")
    
    print("All tests completed")

if __name__ == "__main__":
    main()
