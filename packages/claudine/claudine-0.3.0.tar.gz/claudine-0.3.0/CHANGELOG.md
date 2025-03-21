# Changelog

All notable changes to the Claudine project will be documented in this file.

## [0.3.0] - 2025-04-01

### Added
- Support for Claude Sonnet 3.7 model (claude-3-7-sonnet-20250219)
- Flexible model configuration parameters

### Updated
- README with specific information about supported models
- Improved API for accessing token and cost information with direct attribute access
- Removed built-in text_editor_wrapper in favor of allowing users to implement their own
- Removed model selection methods (set_model) in favor of configuration at initialization

### Fixed
- Documentation clarity around caching behavior and token usage

## [0.2.0] - 2025-03-16

### Added
- Comprehensive token tracking system with cache-related metrics
- Cache support for optimizing API usage and reducing costs
- `cache_delta` feature in TokenCost class to track cost savings from using cache
- New modular project structure with dedicated packages for tokens, tools, and API
- Centralized constants module in API package for better organization
- Enhanced token tracking with cache-related metrics

### Updated
- README with information about cache support and cost tracking
- Enhanced API call logging in verbose mode
- TokenUsageInfo.calculate_cost method to include cache_delta calculations
- Renamed `process_prompt` method to `query` for more intuitive API
- Improved API consistency with better naming:
  - Renamed `ApiClient` to `ClaudeClient`
  - Renamed `TokenTracker` to `TokenManager`
  - Renamed `get_token_usage()` to `get_tokens()`
  - Renamed `get_cost()` to `get_token_cost()`
  - Renamed `debug_mode` parameter to `verbose`
  - Renamed `instructions` parameter to `system_prompt`
  - Renamed `max_rounds` to `max_tool_rounds`
  - Renamed exceptions for clarity: `MaxTokensExceededException` → `TokenLimitExceededException` and `MaxRoundsExceededException` → `ToolRoundsLimitExceededException`
- Reorganized codebase into modular packages for better maintainability
- Enhanced token usage tracking with detailed cost calculations
- Improved error handling with more descriptive exception names
- Renamed example file from `debug_mode_example.py` to `verbose_mode_example.py`
- Updated all example files to use the new API naming conventions

## [0.1.1] - 2023-12-15

Initial release with basic functionality:
- Claude API integration
- Basic token tracking
- Tool usage support
- Simple conversation management
