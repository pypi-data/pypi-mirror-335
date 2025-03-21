"""
Token-related data models for Claude API.

This module defines the data structures used for token tracking,
pricing, and cost calculations.
"""

from dataclasses import dataclass
from typing import Dict

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
    
    def calculate_cost(self, pricing: ModelPricing) -> Dict[str, float]:
        """
        Calculate cost based on token usage and pricing, including cache costs.
        
        Cache writes cost 25% more than base input tokens.
        Cache reads cost only 10% of the base input token price.
        
        Returns:
            Dictionary with cost breakdown by token type
        """
        # Standard token costs
        input_cost = pricing.input_tokens.calculate_cost(self.input_tokens)
        output_cost = pricing.output_tokens.calculate_cost(self.output_tokens)
        
        # Cache-related costs
        cache_creation_cost = pricing.input_tokens.calculate_cost(self.cache_creation_input_tokens) * 1.25
        cache_read_cost = pricing.input_tokens.calculate_cost(self.cache_read_input_tokens) * 0.10
        
        # Total cost including cache
        total_cost = input_cost + output_cost + cache_creation_cost + cache_read_cost
        
        return {
            "input_cost": input_cost,
            "output_cost": output_cost,
            "cache_creation_cost": cache_creation_cost,
            "cache_read_cost": cache_read_cost,
            "total_cost": total_cost
        }

@dataclass
class TokenCost:
    """
    Represents cost information for token usage.
    """
    input_cost: float = 0.0
    output_cost: float = 0.0
    cache_creation_cost: float = 0.0
    cache_read_cost: float = 0.0
    unit: str = "USD"
    cache_delta: float = 0.0  # Cost savings from using cache vs. standard pricing
    
    @property
    def total_cost(self) -> float:
        """Calculate total cost across all token types"""
        return self.input_cost + self.output_cost + self.cache_creation_cost + self.cache_read_cost

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
        """
        Get combined total usage across text and tools
        """
        return TokenUsage(
            input_tokens=self.text_usage.input_tokens + self.tools_usage.input_tokens,
            output_tokens=self.text_usage.output_tokens + self.tools_usage.output_tokens,
            cache_creation_input_tokens=(
                self.text_usage.cache_creation_input_tokens + 
                self.tools_usage.cache_creation_input_tokens
            ),
            cache_read_input_tokens=(
                self.text_usage.cache_read_input_tokens + 
                self.tools_usage.cache_read_input_tokens
            )
        )
    
    def calculate_cost(self, pricing: ModelPricing) -> Dict[str, TokenCost]:
        """
        Calculate costs for all token usage based on provided pricing.
        
        Returns:
            Dictionary with text_cost, tools_cost, total_cost and by_tool costs
        """
        # Calculate text costs
        text_cost_dict = self.text_usage.calculate_cost(pricing)
        
        # Calculate text cache delta
        text_standard_cost = pricing.input_tokens.calculate_cost(
            self.text_usage.input_tokens + 
            self.text_usage.cache_creation_input_tokens + 
            self.text_usage.cache_read_input_tokens
        )
        text_actual_cost = text_cost_dict["input_cost"] + text_cost_dict["cache_creation_cost"] + text_cost_dict["cache_read_cost"]
        text_cache_delta = text_standard_cost - text_actual_cost
        
        text_cost = TokenCost(
            input_cost=text_cost_dict["input_cost"],
            output_cost=text_cost_dict["output_cost"],
            cache_creation_cost=text_cost_dict["cache_creation_cost"],
            cache_read_cost=text_cost_dict["cache_read_cost"],
            cache_delta=text_cache_delta,
            unit=pricing.input_tokens.unit
        )
        
        # Calculate tools costs
        tools_cost_dict = self.tools_usage.calculate_cost(pricing)
        
        # Calculate tools cache delta
        tools_standard_cost = pricing.input_tokens.calculate_cost(
            self.tools_usage.input_tokens + 
            self.tools_usage.cache_creation_input_tokens + 
            self.tools_usage.cache_read_input_tokens
        )
        tools_actual_cost = tools_cost_dict["input_cost"] + tools_cost_dict["cache_creation_cost"] + tools_cost_dict["cache_read_cost"]
        tools_cache_delta = tools_standard_cost - tools_actual_cost
        
        tools_cost = TokenCost(
            input_cost=tools_cost_dict["input_cost"],
            output_cost=tools_cost_dict["output_cost"],
            cache_creation_cost=tools_cost_dict["cache_creation_cost"],
            cache_read_cost=tools_cost_dict["cache_read_cost"],
            cache_delta=tools_cache_delta,
            unit=pricing.input_tokens.unit
        )
        
        # Calculate total cache delta
        total_cache_delta = text_cache_delta + tools_cache_delta
        
        # Calculate total cost
        total_cost = TokenCost(
            input_cost=text_cost.input_cost + tools_cost.input_cost,
            output_cost=text_cost.output_cost + tools_cost.output_cost,
            cache_creation_cost=text_cost.cache_creation_cost + tools_cost.cache_creation_cost,
            cache_read_cost=text_cost.cache_read_cost + tools_cost.cache_read_cost,
            cache_delta=total_cache_delta,
            unit=pricing.input_tokens.unit
        )
        
        # Calculate by-tool costs if available
        by_tool_costs = {}
        if self.by_tool:
            for tool_name, tool_usage in self.by_tool.items():
                tool_cost_dict = tool_usage.calculate_cost(pricing)
                
                # Calculate tool cache delta
                tool_standard_cost = pricing.input_tokens.calculate_cost(
                    tool_usage.input_tokens + 
                    tool_usage.cache_creation_input_tokens + 
                    tool_usage.cache_read_input_tokens
                )
                tool_actual_cost = tool_cost_dict["input_cost"] + tool_cost_dict["cache_creation_cost"] + tool_cost_dict["cache_read_cost"]
                tool_cache_delta = tool_standard_cost - tool_actual_cost
                
                by_tool_costs[tool_name] = TokenCost(
                    input_cost=tool_cost_dict["input_cost"],
                    output_cost=tool_cost_dict["output_cost"],
                    cache_creation_cost=tool_cost_dict["cache_creation_cost"],
                    cache_read_cost=tool_cost_dict["cache_read_cost"],
                    cache_delta=tool_cache_delta,
                    unit=pricing.input_tokens.unit
                )
        
        return {
            "text_cost": text_cost,
            "tools_cost": tools_cost,
            "total_cost": total_cost,
            "by_tool": by_tool_costs
        }