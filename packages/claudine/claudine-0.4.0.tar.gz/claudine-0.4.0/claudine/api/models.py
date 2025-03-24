"""
Data models for API requests and responses.
"""
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from ..tokens.models import TokenCost

@dataclass
class ToolUseResponse:
    """
    Represents a tool use response from Claude.
    """
    type: str = "tool_use"
    name: str = ""
    input: Dict[str, Any] = None
    id: str = ""
    message_id: str = ""

@dataclass
class TextResponse:
    """
    Represents a text response from Claude.
    """
    type: str = "text"
    text: str = ""
    message_id: str = ""
    was_truncated: bool = False

@dataclass
class TokenPricing:
    """
    Represents pricing information for tokens.
    """
    cost_per_million_tokens: float = 0.0
    unit: str = "USD"
    
    def calculate_cost(self, tokens: int) -> float:
        """Calculate cost for a given number of tokens"""
        return (tokens / 1_000_000) * self.cost_per_million_tokens

@dataclass
class ModelPricing:
    """
    Represents pricing information for a model.
    """
    input_tokens: TokenPricing
    output_tokens: TokenPricing
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate total cost for input and output tokens"""
        input_cost = self.input_tokens.calculate_cost(input_tokens)
        output_cost = self.output_tokens.calculate_cost(output_tokens)
        return input_cost + output_cost

@dataclass
class TokenUsage:
    """
    Represents token usage information.
    """
    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0
    
    @property
    def total_tokens(self) -> int:
        """Calculate total tokens from input and output tokens"""
        return self.input_tokens + self.output_tokens
    
    @property
    def total_cache_tokens(self) -> int:
        """Calculate total cache-related tokens"""
        return self.cache_creation_input_tokens + self.cache_read_input_tokens
    
    def calculate_cost(self, pricing: ModelPricing) -> float:
        """Calculate cost based on token usage and pricing"""
        return pricing.calculate_cost(self.input_tokens, self.output_tokens)



@dataclass
class TokenUsageInfo:
    """
    Comprehensive token usage information including text and tool usage.
    """
    text_usage: TokenUsage
    tools_usage: TokenUsage
    by_tool: Dict[str, TokenUsage] = None
    
    @property
    def total_usage(self) -> TokenUsage:
        """Get combined total usage across text and tools"""
        return TokenUsage(
            input_tokens=self.text_usage.input_tokens + self.tools_usage.input_tokens,
            output_tokens=self.text_usage.output_tokens + self.tools_usage.output_tokens,
            cache_creation_input_tokens=self.text_usage.cache_creation_input_tokens + self.tools_usage.cache_creation_input_tokens,
            cache_read_input_tokens=self.text_usage.cache_read_input_tokens + self.tools_usage.cache_read_input_tokens
        )
    
    def calculate_cost(self, pricing: ModelPricing) -> Dict[str, TokenCost]:
        """
        Calculate costs for all token usage based on provided pricing.
        
        Returns:
            Dictionary with text_cost, tools_cost, total_cost and by_tool costs
        """
        # Use the implementation from tokens.models
        from ..tokens.models import TokenUsageInfo as TokenModelsUsageInfo
        
        # Create a TokenUsageInfo instance from tokens.models
        token_models_usage_info = TokenModelsUsageInfo(
            text_usage=self.text_usage,
            tools_usage=self.tools_usage,
            by_tool=self.by_tool
        )
        
        # Use the implementation from tokens.models
        return token_models_usage_info.calculate_cost(pricing)

ResponseType = Union[ToolUseResponse, TextResponse]
