#!/usr/bin/env python3
"""Main entry point for the lambda_deploy package."""

import sys
from lambda_deploy.cli import cli

if __name__ == "__main__":
    sys.exit(cli())
