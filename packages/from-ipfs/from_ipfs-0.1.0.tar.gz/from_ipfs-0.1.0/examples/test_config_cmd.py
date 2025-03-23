"""
Test the from_ipfs config command.

This script specifically tests the newly added config command
to ensure it displays the correct configuration information.
"""

import os
import subprocess


def run_config_command():
    """Run the config command and print the output."""
    print("Testing 'from_ipfs config' command...")
    cmd = "from_ipfs config"

    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: Command failed with exit code {e.returncode}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False


def main():
    """Main entry point for testing the config command."""
    print("Testing the from_ipfs config command...")

    # First run without environment variables
    success = run_config_command()

    if not success:
        print("Config command test failed")
        return

    # Test with custom environment variables
    print("\nTesting with custom environment variables...")

    # Set custom environment variables
    custom_env = os.environ.copy()
    custom_env["FROM_IPFS_CACHE"] = "/tmp/test_from_ipfs_cache"
    custom_env["FROM_IPFS_GATEWAYS"] = (
        "https://test-gateway.com/ipfs/,https://another-gateway.com/ipfs/"
    )

    cmd = "from_ipfs config"
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True, env=custom_env
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: Command failed with exit code {e.returncode}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False


if __name__ == "__main__":
    main()
