# Claudine Architecture Proposal

As the `agent.py` file is growing larger, here's a proposed reorganization to improve modularity and maintainability.

## Current Structure
Currently, most functionality is contained in the `agent.py` file, which includes:
- The main `Agent` class
- Tool management logic
- API interaction
- Token tracking integration

## Proposed Structure

```
claudine/
├── __init__.py
├── agent.py              # Main Agent class (simplified)
├── api/
│   ├── __init__.py
│   ├── client.py         # API client wrapper
│   └── models.py         # Data models for API requests/responses
├── tools/
│   ├── __init__.py
│   ├── manager.py        # Tool registration and execution
│   ├── schema.py         # Tool schema generation
│   └── callbacks.py      # Tool callback functionality
├── token_tracking.py     # Token tracking (already separate)
└── utils/
    ├── __init__.py
    └── helpers.py        # Common utility functions
```

## Component Responsibilities

### agent.py
- Main `Agent` class with a simplified interface
- Orchestrates the interaction between components
- Maintains conversation state

### api/client.py
- Wraps the Anthropic API client
- Handles API call parameters
- Processes API responses

### api/models.py
- Defines data models for API requests and responses
- Provides type hints and validation

### tools/manager.py
- Handles tool registration and execution
- Manages tool schemas
- Processes tool calls and results

### tools/schema.py
- Generates JSON schemas for tools
- Validates tool inputs and outputs

### tools/callbacks.py
- Implements tool callback functionality
- Provides pre/post execution hooks

### token_tracking.py
- Tracks token usage (already implemented)

### utils/helpers.py
- Common utility functions
- Shared helper methods

## Migration Strategy

1. Create the directory structure
2. Extract the `ToolManager` class to `tools/manager.py`
3. Move API interaction code to `api/client.py`
4. Create data models in `api/models.py`
5. Refactor the `Agent` class to use the new components
6. Update imports in all files

This modular approach will make the codebase more maintainable, testable, and easier to extend with new features.
