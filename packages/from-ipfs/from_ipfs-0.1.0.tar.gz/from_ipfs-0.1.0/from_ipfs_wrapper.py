#!/usr/bin/env python3

import os
import sys

from from_ipfs.cli import main

# Get the absolute path of the script
script_path = os.path.abspath(__file__)
print(f"Script path: {script_path}")

# Get the directory containing the script
script_dir = os.path.dirname(script_path)
print(f"Script directory: {script_dir}")

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(script_dir))
print(f"Added to Python path: {os.path.dirname(script_dir)}")

# Show environment variables
print("\nEnvironment variables:")
for key, value in os.environ.items():
    print(f"{key}={value}")

if __name__ == "__main__":
    sys.exit(main())
