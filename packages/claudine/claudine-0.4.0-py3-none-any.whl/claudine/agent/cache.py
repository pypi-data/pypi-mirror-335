"""
Cache-related functionality for the Agent class.

This module re-exports functionality from the tokens.cache module.
"""
from typing import Dict, List
from ..tokens.cache import add_cache_control_to_messages

# Re-export add_cache_control_to_messages from tokens.cache
__all__ = ["add_cache_control_to_messages"]
