#!/usr/bin/env python3
"""Info command."""

import click

from lambda_deploy.core.deployer import LambdaDeployer
from lambda_deploy.utils.logging import log, colorize


@click.command()
@click.option('--stage', envvar='STAGE', required=True, help='Deployment stage (dev, stg, prd)')
@click.option('--config-dir', default='.config', help='Directory containing configuration files')
@click.option('--release', envvar='RELEASE', help='Release identifier (git commit hash)')
def info(stage, config_dir, release):
    """display Lambda function configuration"""
    log(f"Retrieving information for stage: {colorize(stage, 'BRIGHT_GREEN')}")
    deployer = LambdaDeployer(stage, config_dir=config_dir, release=release)
    deployer.show_info()
