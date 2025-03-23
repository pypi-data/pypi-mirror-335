"""
Command-line interface for from_ipfs package.
"""

import argparse
import os
import sys

from . import __version__
from .utils import clear_cache, download_from_ipfs, list_cached_models, show_config


def download_command(args: argparse.Namespace) -> None:
    """
    Download a model from IPFS.

    Args:
        args: Command-line arguments
    """
    try:
        local_path = download_from_ipfs(args.uri, args.filepath)
        print(f"Downloaded to: {local_path}")
    except Exception as e:
        print(f"Error downloading model: {e}")
        sys.exit(1)


def list_command(args: argparse.Namespace) -> None:
    """
    List cached models.

    Args:
        args: Command-line arguments
    """
    models = list_cached_models()

    if not models:
        print("No cached models found.")
        return

    print(f"Cached models ({len(models)}):")
    for model in models:
        print(f"  - ipfs://{model}")


def clear_command(args: argparse.Namespace) -> None:
    """
    Clear the model cache.

    Args:
        args: Command-line arguments
    """
    try:
        clear_cache(args.cid)
    except Exception as e:
        print(f"Error clearing cache: {e}")
        sys.exit(1)


def config_command(args: argparse.Namespace) -> None:
    """
    Show the current configuration.

    Args:
        args: Command-line arguments
    """
    print("Config command invoked via CLI")
    show_config()


def create_parser():
    """Create the argument parser with all commands"""
    parser = argparse.ArgumentParser(
        prog="from_ipfs",
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
    config_parser = subparsers.add_parser("config", help="Show current configuration")

    # Add config explicitly to the choices to prevent parsing issues
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            action.choices["config"] = config_parser

    # Debug output
    print("DEBUG: Parser created with the following subparsers:")
    for action in parser._subparsers._actions:
        if isinstance(action, argparse._SubParsersAction):
            for cmd, subparser in action.choices.items():
                print(f"DEBUG:   - {cmd}: {subparser}")

    return parser


def main():
    """Main entry point for the CLI."""

    # Try to import transformers and patch it
    try:
        from from_ipfs import patch_transformers

        patch_transformers()
    except ImportError:
        print("transformers not installed, skipping patching")

    # Try to import llama_cpp and patch it
    try:
        from from_ipfs import patch_llama_cpp

        patch_llama_cpp()
    except ImportError:
        print("llama-cpp-python not installed, skipping patching")

    # Debug output for process and arguments
    process_name = os.path.basename(sys.argv[0])
    print(f"DEBUG: Running from process: {process_name}")
    print(f"DEBUG: Full sys.argv = {sys.argv}")

    # Special handling for 'config' command before any parsing
    if len(sys.argv) > 1 and sys.argv[1] == "config":
        print(f"DEBUG: Detected direct 'config' command from sys.argv[1] = {sys.argv[1]}")
        config_command(None)
        return 0

    # Normal argument parsing
    parser = create_parser()

    # Custom handling for specific cases where argparse might fail
    if len(sys.argv) == 1:
        print("DEBUG: No arguments provided, showing help")
        parser.print_help()
        return 1

    # Attempt to parse arguments normally
    try:
        args = parser.parse_args()
        print(f"DEBUG: Parsed arguments = {args}")
    except SystemExit:
        # If parsing fails, check if it might be the config command
        if len(sys.argv) > 1 and "config" in sys.argv[1]:
            print("DEBUG: Parsing failed but detected 'config' in argument, running config command")
            config_command(None)
            return 0
        raise

    if not args.command:
        print("DEBUG: No command specified in parsed args")
        parser.print_help()
        return 1

    try:
        # Handle the "download" command
        if args.command == "download":
            download_command(args)

        # Handle the "list" command
        elif args.command == "list":
            list_command(args)

        # Handle the "clear" command
        elif args.command == "clear":
            clear_command(args)

        # Handle the "config" command
        elif args.command == "config":
            print("DEBUG: config command detected via argparse")
            config_command(args)

        else:
            print(f"DEBUG: Unrecognized command: {args.command}")
            parser.print_help()
            return 1

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
