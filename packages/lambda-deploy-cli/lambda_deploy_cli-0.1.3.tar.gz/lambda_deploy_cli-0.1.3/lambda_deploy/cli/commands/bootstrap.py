#!/usr/bin/env python3
"""Bootstrap command."""

import click

from lambda_deploy.core.deployer import LambdaDeployer
from lambda_deploy.utils.logging import log, colorize, success


@click.command()
@click.option('--stage', envvar='STAGE', required=True, help='Deployment stage (dev, stg, prd)')
@click.option('--config-dir', default='.config', help='Directory containing configuration files')
@click.option('--release', envvar='RELEASE', help='Release identifier (git commit hash)')
@click.option('--skip-validation', is_flag=True, help='Skip AWS credentials validation')
def bootstrap(stage, config_dir, release, skip_validation):
    """Bootstrap config templates.
    Processes config templates defined in the configs section,
    loads template files, resolves variables, and writes to destinations.
    """
    log(f"Bootstrapping configuration for stage: {colorize(stage, 'BRIGHT_GREEN')}")

    deployer = LambdaDeployer(
        stage,
        config_dir=config_dir,
        release=release,
        skip_validation=skip_validation
    )
    deployer.bootstrap()

    success("Bootstrap completed successfully!")
