#!/usr/bin/env python3
"""
Standalone script to display the configuration for from_ipfs.
This is useful when the main CLI entry point doesn't recognize the 'config' command.
"""

import sys

from from_ipfs.utils import show_config


def main():
    """Display the from_ipfs configuration."""
    show_config()
    return 0


if __name__ == "__main__":
    sys.exit(main())
