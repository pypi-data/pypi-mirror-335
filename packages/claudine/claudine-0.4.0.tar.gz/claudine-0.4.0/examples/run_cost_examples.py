#!/usr/bin/env python3
"""
Script to run the examples that demonstrate cost information.
"""
import os
import subprocess
import sys
from pathlib import Path

def run_example(example_path):
    """Run a single example file using python and return its exit code."""
    print(f"\n{'=' * 80}")
    print(f"Running example: {example_path.name}")
    print(f"{'=' * 80}")
    
    result = subprocess.run([sys.executable, str(example_path)], capture_output=False)
    
    print(f"\nExit code: {result.returncode}")
    if result.returncode != 0:
        print(f"Error running {example_path.name}. Stopping execution.")
        sys.exit(result.returncode)
    return result.returncode

def main():
    """Run the cost-related example files."""
    # Get the directory of this script
    examples_dir = Path(__file__).parent
    
    # List of examples that demonstrate cost information
    cost_examples = [
        "token_tracker.py",
        "token_usage.py",
        "token_usage_tracking.py",
        "token_usage_with_tools.py",
        "tool_token_tracking.py",
        "agent_with_token_tracking.py"
    ]
    
    # Convert to full paths
    example_files = [examples_dir / example for example in cost_examples]
    
    print(f"Found {len(example_files)} cost-related examples to run")
    
    # Run each example
    for example_file in example_files:
        if example_file.exists():
            run_example(example_file)
        else:
            print(f"Warning: Example file {example_file.name} not found")
    
    print("\n" + "=" * 80)
    print("All cost-related examples ran successfully!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
