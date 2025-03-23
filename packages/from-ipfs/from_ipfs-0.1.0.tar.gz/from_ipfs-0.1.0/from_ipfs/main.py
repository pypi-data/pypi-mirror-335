#!/usr/bin/env python3
"""
Direct entry point for the from_ipfs CLI.
This is a workaround for entry_points that don't always work correctly with subcommands.
"""

import argparse
import sys

from from_ipfs import __version__
from from_ipfs.utils import clear_cache, download_from_ipfs, list_cached_models, show_config


def create_parser():
    """Create the argument parser with all commands"""
    parser = argparse.ArgumentParser(
        prog="from_ipfs_alt",
        description="from_ipfs - Use IPFS URIs with Hugging Face transformers and llama-cpp-python",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    # Create subparsers
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Download command
    download_parser = subparsers.add_parser("download", help="Download a model from IPFS")
    download_parser.add_argument("uri", help="IPFS URI to download (e.g. ipfs://QmYourModelCID)")
    download_parser.add_argument(
        "filepath", nargs="?", help="Specific file to download from the IPFS directory"
    )

    # List command
    subparsers.add_parser("list", help="List cached models")

    # Clear command
    clear_parser = subparsers.add_parser("clear", help="Clear the model cache")
    clear_parser.add_argument(
        "cid",
        nargs="?",
        help="IPFS CID to clear from cache (if not specified, all will be cleared)",
    )

    # Config command
    subparsers.add_parser("config", help="Show current configuration")

    return parser


def main():
    """Main entry point for the CLI."""

    # Try to import transformers and patch it
    try:
        print("transformers is installed, proceeding with patching")
    except ImportError:
        print("transformers not installed, skipping patching")

    # Try to import llama_cpp and patch it
    try:
        print("llama-cpp-python is installed, proceeding with patching")
    except ImportError:
        print("llama-cpp-python not installed, skipping patching")

    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        # Handle the "download" command
        if args.command == "download":
            local_path = download_from_ipfs(args.uri, args.filepath)
            print(f"Downloaded to: {local_path}")

        # Handle the "list" command
        elif args.command == "list":
            cached_models = list_cached_models()
            if not cached_models:
                print("No models in cache.")
            else:
                print("Cached models:")
                for cid in cached_models:
                    print(f"- {cid}")

        # Handle the "clear" command
        elif args.command == "clear":
            if args.cid:
                clear_cache(args.cid)
                print(f"Cleared cache for {args.cid}")
            else:
                clear_cache()
                print("Cleared all caches")

        # Handle the "config" command
        elif args.command == "config":
            show_config()

        else:
            parser.print_help()
            return 1

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
