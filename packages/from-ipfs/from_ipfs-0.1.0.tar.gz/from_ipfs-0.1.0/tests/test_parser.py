import argparse

from from_ipfs.cli import create_parser


def main():
    parser = create_parser()
    for action in parser._subparsers._actions:
        if isinstance(action, argparse._SubParsersAction):
            print("Available commands:")
            for cmd, subparser in action.choices.items():
                print(f"  - {cmd}: {subparser}")


if __name__ == "__main__":
    main()
