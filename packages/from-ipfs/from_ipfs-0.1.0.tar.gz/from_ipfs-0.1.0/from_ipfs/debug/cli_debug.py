#!/usr/bin/env python3
import sys

from from_ipfs.cli import main

if __name__ == "__main__":
    sys.argv = ["from_ipfs", "config"]
    print(f"Running CLI with args: {sys.argv}")
    main()
