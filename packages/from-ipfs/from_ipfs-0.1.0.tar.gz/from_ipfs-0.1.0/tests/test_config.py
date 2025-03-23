#!/usr/bin/env python3


from from_ipfs.cli import config_command


class MockArgs:
    pass


args = MockArgs()
config_command(args)
