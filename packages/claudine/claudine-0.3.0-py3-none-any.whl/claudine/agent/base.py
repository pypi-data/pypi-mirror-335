"""
Core Agent class for Claudine.
Provides a high-level interface for interacting with Claude models,
with support for tool use, token tracking, and conversation management.
"""
from typing import Dict, List, Optional, Callable, Any, Union
import os
import json
import time
from datetime import datetime
from uuid import uuid4

from ..api.client import ClaudeClient
from ..api.models import ResponseType, ToolUseResponse, TextResponse
from ..api.constants import DEFAULT_MODEL
from ..tools.manager import ToolManager
from ..tokens.tracking import TokenManager
from ..tokens.models import TokenUsage, TokenUsageInfo, TokenCost
from ..utils.helpers import generate_message_id, extract_text_content, format_tool_result
from ..exceptions import TokenLimitExceededException, ToolRoundsLimitExceededException

from .cache import add_cache_control_to_messages
from .messaging import extract_tool_info, process_response_content, filter_tool_messages

class Agent:
    """
    Agent for interacting with Claude.
    """
    
    def __init__(self, api_key: Optional[str] = None, 
                max_tokens: int = 1024, config_params: Optional[Dict[str, Any]] = None,
                max_tool_rounds: int = 30, system_prompt: Optional[str] = None,
                tools: Optional[List[Callable]] = None,
                callbacks: Optional[Dict[str, Callable]] = None,
                disable_parallel_tool_use: bool = True,
                text_editor_tool: Optional[Callable] = None,
                bash_tool: Optional[Callable] = None,
                verbose: bool = False):
        """
        Initialize the Agent wrapper with your Anthropic API key, model parameters, and tools.
        If api_key is not provided, it will use the ANTHROPIC_API_KEY environment variable.
        
        Args:
            api_key: Anthropic API key
            max_tokens: Maximum number of tokens to generate
            config_params: Dictionary of configuration parameters for the model (top_k, top_p, etc.)
            max_tool_rounds: Maximum number of rounds for tool use
            system_prompt: Instructions to guide the model's behavior (used as system prompt)
            tools: List of functions to register as tools
            callbacks: Dictionary of callback functions: {"pre_tool": pre_tool_callback, "post_tool": post_tool_callback, "text": text_callback}
            disable_parallel_tool_use: Disable parallel tool use to ensure accurate token accounting
            text_editor_tool: Callable function to handle text editor tool requests. Must implement the
                         commands and response formats as specified in the Anthropic documentation:
                         https://docs.anthropic.com/en/docs/build-with-claude/tool-use/text-editor-tool
            bash_tool: Callable function to handle bash command tool requests. Must implement the
                         command execution and response formats for bash commands.
            verbose: If True, print debug information about API calls
        """
        # Initialize API client
        self.claude_client = ClaudeClient(api_key=api_key, verbose=verbose)
        
        # Initialize conversation state
        self.messages = []
        self.max_tokens = max_tokens
        
        # Handle config parameters
        self.config_params = config_params or {}
            
        self.max_tool_rounds = max_tool_rounds
        self.system = system_prompt
        
        # Initialize token tracker
        self.token_manager = TokenManager(verbose=verbose)
        
        # Extract tool callbacks if provided
        pre_callback = None
        post_callback = None
        text_callback = None
        if callbacks:
            pre_callback = callbacks.get("pre_tool")
            post_callback = callbacks.get("post_tool")
            text_callback = callbacks.get("text")
            
        # Initialize tool manager with callbacks
        self.tool_manager = ToolManager(
            pre_callback=pre_callback, 
            post_callback=post_callback,
            text_callback=text_callback
        )
        
        # Register tools if provided
        if tools:
            self.tool_manager.register_tools(tools)
        
        # Register text editor tool if provided
        if text_editor_tool:
            self.tool_manager.tools["str_replace_editor"] = text_editor_tool
            self.tool_manager.text_editor_tool = text_editor_tool
            
        # Register bash tool if provided
        if bash_tool:
            self.tool_manager.tools["bash"] = bash_tool
            self.tool_manager.bash_tool = bash_tool
        
        # Disable parallel tool use to ensure accurate token accounting
        self.disable_parallel_tool_use = disable_parallel_tool_use
    
    def _call_claude(self, tools: Optional[List[Dict]] = None) -> Union[ToolUseResponse, TextResponse]:
        """
        Call Claude with the current conversation history.
        
        Args:
            tools: Optional list of tool schemas to include
            
        Returns:
            Response from Claude, either a tool use request or a text response
        """
        # Set tool_choice with disable_parallel_tool_use parameter
        tool_choice = None
        if tools:
            tool_choice = {
                "type": "auto",
                "disable_parallel_tool_use": self.disable_parallel_tool_use
            }
        
        # Process messages to add cache control attributes
        processed_messages = add_cache_control_to_messages(self.messages)
        
        # Debug information before API call
        if self.claude_client.verbose:
            print("\n[DEBUG] Calling Claude API")
            print(f"  Model: {DEFAULT_MODEL}")
            print(f"  Max tokens: {self.max_tokens}")
            print(f"  Config params: {self.config_params}")
            print(f"  Number of messages: {len(processed_messages)}")
            print(f"  Tools enabled: {bool(tools)}")
            if tools:
                print(f"  Number of tools: {len(tools)}")
                print(f"  Tool names: {', '.join([t.get('name', 'unnamed') for t in tools])}")
                print(f"  Parallel tool use: {not self.disable_parallel_tool_use}")
        
        # Make the API call
        response = self.claude_client.create_message(
            model=DEFAULT_MODEL,
            messages=processed_messages,
            max_tokens=self.max_tokens,
            config_params=self.config_params,
            system=self.system,
            tools=tools,
            tool_choice=tool_choice
        )
        
        # Debug information after API call
        if self.claude_client.verbose:
            print("\n[DEBUG] Claude API Response")
            print(f"  Message ID: {response.id}")
            print(f"  Stop reason: {response.stop_reason}")
            print(f"  Input tokens: {response.usage.input_tokens}")
            print(f"  Output tokens: {response.usage.output_tokens}")
            print(f"  Cache creation tokens: {response.usage.cache_creation_input_tokens}")
            print(f"  Cache read tokens: {response.usage.cache_read_input_tokens}")
        
        # Track token usage
        message_id = response.id
        
        # Extract tool-related information
        is_tool_related, tool_name, parent_message_id = extract_tool_info(self.messages)
        
        self.token_manager.add_message(
            message_id=message_id,
            usage=response.usage,
            is_tool_related=is_tool_related,
            tool_name=tool_name,
            parent_message_id=parent_message_id
        )
        
        # Check if token limit was reached
        was_truncated = response.stop_reason == "max_tokens"
        
        # Process each content block, call text callback for text blocks, and add text to conversation
        text_content = process_response_content(response)
        
        # If we have text content, add it to the conversation and call text callback
        if text_content:
            self.messages.append({
                "role": "assistant",
                "content": text_content
            })
            
            # Call text callback if available
            if self.tool_manager.text_callback:
                self.tool_manager.text_callback(text_content)
        
        # Check if tool use is requested
        if response.stop_reason == "tool_use":
            # Find the tool use block
            tool_use = None
            for content_block in response.content:
                if content_block.type == "tool_use":
                    tool_use = content_block
                    break
            
            if tool_use:
                return ToolUseResponse(
                    type="tool_use",
                    name=tool_use.name,
                    input=tool_use.input,
                    id=tool_use.id,
                    message_id=message_id
                )
        
        # Regular text response
        text_content = extract_text_content(response.content)
        
        # If the response was truncated due to token limits, raise an exception
        if was_truncated:
            raise TokenLimitExceededException(
                message=f"Response was truncated because it reached the maximum token limit of {self.max_tokens}",
                response_text=text_content
            )
        
        return TextResponse(
            type="text",
            text=text_content,
            message_id=message_id,
            was_truncated=was_truncated
        )
    
    def query(self, prompt: str) -> str:
        """
        Query Claude with a prompt and return the response.
        
        Args:
            prompt: User prompt
            
        Returns:
            Claude's response as a string
            
        Raises:
            TokenLimitExceededException: If the response was truncated due to token limits
            ToolRoundsLimitExceededException: If the maximum number of tool execution rounds was reached
        """
        # Add user message to conversation
        self.messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Get tool schemas
        tools = self.tool_manager.get_tool_schemas()
        
        # Call Claude
        response = self._call_claude(tools)
        
        # If tool use is requested, execute the tool
        rounds = 0
        while response.type == "tool_use" and rounds < self.max_tool_rounds:
            # Add assistant message with tool use
            content_items = []
            
            content_items.append({
                "type": "tool_use",
                "id": response.id,
                "name": response.name,
                "input": response.input
            })
            
            self.messages.append({
                "role": "assistant",
                "content": content_items
            })
            
            # Execute the tool
            tool_result = self.tool_manager.execute_tool(response.name, response.input)
            
            # Add user message with tool result
            self.messages.append({
                "role": "user",
                "content": [
                    format_tool_result(response.id, tool_result)
                ]
            })
            
            # Call Claude again
            response = self._call_claude(tools)
            
            # Increment rounds
            rounds += 1
        
        # Check if we hit the max rounds limit
        if rounds >= self.max_tool_rounds:
            # Check the response type before accessing text attribute
            response_text = response.text if hasattr(response, 'text') else ""
            raise ToolRoundsLimitExceededException(response_text=response_text, rounds=rounds)
        
        # Return the response text
        return response.text
    
    def get_tokens(self) -> TokenUsageInfo:
        """
        Get token usage information.
        
        Returns:
            TokenUsageInfo object with usage details
        """
        return self.token_manager.get_token_usage()
    
    def get_token_cost(self) -> TokenCost:
        """
        Get token cost information.
        
        Returns:
            TokenCost object with cost details
        """
        return self.token_manager.get_cost()
    
    def reset(self):
        """Reset the conversation history."""
        self.messages = []
        self.token_manager.reset()
        
    def get_messages(self, filter_out_tools: bool = False) -> List[Dict]:
        """
        Get the current conversation messages.
        
        Args:
            filter_out_tools: If True, removes messages related to tool calls or tool results
        
        Returns:
            A copy of the conversation messages list
        """
        messages = self.messages.copy()
        
        if filter_out_tools:
            return filter_tool_messages(messages)
        
        return messages
    
    def set_messages(self, messages: List[Dict]):
        """
        Set the conversation messages.
        
        Args:
            messages: List of message dictionaries to set as the conversation history
        """
        self.messages = messages.copy()
