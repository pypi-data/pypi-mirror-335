"""
Test the from_ipfs CLI functionality.

This script shows how to:
1. Use the CLI to view cached models
2. Use the CLI to manage the cache
3. No actual downloads required - just demonstrates commands

Run this after running some of the other example scripts
that populate the cache with models.
"""

import os
import subprocess


def run_command(cmd, description):
    """Run a command and print the output."""
    print(f"\n{description}:")
    print(f"$ {cmd}")

    # Run the command
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(e.stdout)
        print(e.stderr)
        return None


def main():
    """Test the from_ipfs CLI functionality."""
    print("Testing from_ipfs CLI functionality")

    # Check if the CLI is installed
    run_command("from_ipfs --help", "Showing help message")

    # List models in cache
    run_command("from_ipfs list", "Listing models in cache")

    # If we have a test model from previous examples, show more info
    test_cid = "QmTestModelCID123456789"
    cache_path = os.path.expanduser("~/.cache/from_ipfs")
    test_model_path = os.path.join(cache_path, test_cid)

    if os.path.exists(test_model_path):
        # Show info about a specific model
        run_command(f"from_ipfs info {test_cid}", "Showing info about a specific model")

    # Show the environment configuration
    run_command("from_ipfs config", "Showing environment configuration")

    print("\nTo download a model from IPFS, you would use:")
    print("$ from_ipfs download ipfs://QmModelCID")

    print("\nTo clear the cache, you would use:")
    print("$ from_ipfs clear")

    print("\nTo clear a specific model, you would use:")
    print("$ from_ipfs clear QmModelCID")

    print("\nCLI test complete!")


if __name__ == "__main__":
    main()
