#!/usr/bin/env python
"""
Run examples with UTF-8 encoding to properly display Unicode characters like the cent symbol (¢).
Usage: python run_example.py <example_module_name>
Example: python run_example.py token_cost
"""

import sys
import importlib
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_example.py <example_module_name>")
        print("Example: python run_example.py token_cost")
        return 1
    
    # Set UTF-8 encoding for the terminal
    if sys.platform == "win32":
        os.system("chcp 65001 > nul")
    
    # Import and run the specified example
    example_name = sys.argv[1]
    try:
        module = importlib.import_module(f"claudine.examples.{example_name}")
        return module.main()
    except ImportError:
        print(f"Error: Could not import example module '{example_name}'")
        print("Available examples:")
        for file in os.listdir(os.path.dirname(__file__)):
            if file.endswith(".py") and file != "__init__.py" and file != "run_example.py":
                print(f"  {file[:-3]}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
