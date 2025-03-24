"""
Custom exceptions for the claudine library.
"""

class ClaudineException(Exception):
    """Base exception for all claudine exceptions."""
    pass

class TokenLimitExceededException(ClaudineException):
    """
    Exception raised when the response from Claude is truncated 
    because it reached the maximum token limit.
    """
    def __init__(self, message="Response was truncated because it reached the maximum token limit", 
                 response_text=None):
        self.message = message
        self.response_text = response_text
        super().__init__(self.message)

class ToolRoundsLimitExceededException(ClaudineException):
    """
    Exception raised when the maximum number of tool execution rounds is reached.
    """
    def __init__(self, message="Maximum number of tool execution rounds reached. Some tasks may be incomplete", 
                 response_text=None, rounds=None):
        self.message = message
        self.response_text = response_text
        self.rounds = rounds
        super().__init__(self.message)
