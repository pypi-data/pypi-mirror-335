"""
Pricing models and calculations for token usage.

This module provides functionality for calculating costs
based on token usage and model-specific pricing information.
"""

from typing import Dict, Optional
from .models import ModelPricing, TokenPricing, TokenCost, TokenUsage
from ..api.constants import DEFAULT_MODEL

# Model pricing data
MODEL_PRICING: Dict[str, ModelPricing] = {
    DEFAULT_MODEL: ModelPricing(
        input_tokens=TokenPricing(
            cost_per_million_tokens=3.0,
            unit="USD"
        ),
        output_tokens=TokenPricing(
            cost_per_million_tokens=15.0,
            unit="USD"
        )
    )
}

def get_model_pricing(model: str = DEFAULT_MODEL) -> Optional[ModelPricing]:
    """
    Get pricing information for a specific model.
    
    Args:
        model: Model identifier
        
    Returns:
        ModelPricing object for the specified model or None if not found
    """
    return MODEL_PRICING.get(model)

def calculate_token_cost(
    usage: TokenUsage,
    model: str = DEFAULT_MODEL
) -> TokenCost:
    """
    Calculate cost for token usage based on model pricing.
    
    Args:
        usage: TokenUsage object containing token usage information
        model: Model identifier to use for pricing
        
    Returns:
        TokenCost object with calculated costs
    """
    pricing = get_model_pricing(model)
    if not pricing:
        return TokenCost(
            input_cost=0.0,
            output_cost=0.0,
            cache_creation_cost=0.0,
            cache_read_cost=0.0,
            unit="USD"
        )
    
    # Calculate costs using the updated TokenUsage.calculate_cost method
    cost_dict = usage.calculate_cost(pricing)
    
    return TokenCost(
        input_cost=cost_dict["input_cost"],
        output_cost=cost_dict["output_cost"],
        cache_creation_cost=cost_dict["cache_creation_cost"],
        cache_read_cost=cost_dict["cache_read_cost"],
        unit=pricing.input_tokens.unit
    )

def register_model_pricing(
    model: str,
    input_cost_per_million: float,
    output_cost_per_million: float,
    unit: str = "USD"
) -> None:
    """
    Register pricing information for a new model.
    
    Args:
        model: Model identifier
        input_cost_per_million: Cost per million input tokens
        output_cost_per_million: Cost per million output tokens
        unit: Currency unit (default: USD)
    """
    MODEL_PRICING[model] = ModelPricing(
        input_tokens=TokenPricing(
            cost_per_million_tokens=input_cost_per_million,
            unit=unit
        ),
        output_tokens=TokenPricing(
            cost_per_million_tokens=output_cost_per_million,
            unit=unit
        )
    )