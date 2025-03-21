#!/usr/bin/env python3
"""
Script to run all example files in the claudine project.
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
    """Run all example files in the examples directory."""
    # Get the directory of this script
    examples_dir = Path(__file__).parent
    
    # Check if a specific example was specified
    if len(sys.argv) > 1:
        example_name = sys.argv[1]
        example_path = examples_dir / example_name
        
        # Check if the file exists
        if not example_path.exists():
            print(f"Error: Example file '{example_name}' not found")
            return 1
        
        # Run the example
        return run_example(example_path)
    
    # Find all Python files in the examples directory
    example_files = [
        f for f in examples_dir.glob("*.py") 
        if f.name not in ["run_all_examples.py", "run_cost_examples.py"]
    ]
    
    # Sort files to ensure consistent order
    example_files.sort()
    
    print(f"Found {len(example_files)} example files to run")
    
    # Run each example
    for example_file in example_files:
        run_example(example_file)
    
    print("\n" + "=" * 80)
    print("All examples ran successfully!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
