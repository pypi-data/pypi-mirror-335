#!/usr/bin/env python3
"""Main CLI for Lambda deployment."""

import click
import os

from lambda_deploy.utils.logging import log, debug, error, colorize
from lambda_deploy import __version__
from lambda_deploy.cli.commands import bootstrap, deploy, info


@click.group()
@click.version_option(version=__version__)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def cli(verbose):
    """Lambda deployment cli for AWS Lambda functions"""
    if verbose:
        os.environ['DEBUG'] = '1'
        debug("Verbose mode enabled")

    # print header
    print("\n" + "=" * 80)
    log(f"Lambda Deploy {colorize('v' + __version__, 'BRIGHT_GREEN')}", prefix="")
    print("=" * 80)


# add commands
cli.add_command(bootstrap)
cli.add_command(deploy)
cli.add_command(info)


def main(args=None):
    """Main entry point."""
    try:
        # handle args for click
        if args is not None and not args:
            args = ['lambda-deploy']
        elif args is not None:
            args.insert(0, 'lambda-deploy')

        return cli(args)
    except Exception as e:
        error(f"{str(e)}")
        return 1
