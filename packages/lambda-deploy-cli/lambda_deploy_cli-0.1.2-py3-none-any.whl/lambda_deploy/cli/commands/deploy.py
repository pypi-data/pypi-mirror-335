#!/usr/bin/env python3
"""Deploy command."""

import click

from lambda_deploy.core.deployer import LambdaDeployer
from lambda_deploy.utils.logging import log, colorize


@click.command()
@click.option('--stage', envvar='STAGE', required=True, help='Deployment stage (dev, stg, prd)')
@click.option('--source', help='Source directory containing code to deploy')
@click.option('--env-vars', help='Path to environment variables JSON file')
@click.option('--config-dir', default='.config', help='Directory containing configuration files')
@click.option('--release', envvar='RELEASE', help='Release identifier (git commit hash)')
@click.option('--skip-env-update', is_flag=True, help='Skip updating environment variables')
@click.option('--skip-validation', is_flag=True, help='Skip AWS credentials validation')
def deploy(stage, source, env_vars, config_dir, release, skip_env_update, skip_validation):
    """Deploy Lambda function to AWS.

    Deploys function code and environment variables.
    Uses 'dist' directory by default, override with --source.
    """
    log(f"Deploying Lambda function for stage: {colorize(stage, 'BRIGHT_GREEN')}")

    if source:
        log(f"Using source directory: {colorize(source, 'BRIGHT_GREEN')}")

    if skip_env_update:
        log("Skipping environment variable update", color="YELLOW")

    deployer = LambdaDeployer(
        stage,
        source_dir=source,
        env_vars_path=env_vars,
        config_dir=config_dir,
        release=release,
        skip_validation=skip_validation
    )
    deployer.deploy(skip_env_update=skip_env_update)
