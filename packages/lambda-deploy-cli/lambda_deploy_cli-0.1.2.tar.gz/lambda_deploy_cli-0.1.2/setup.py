#!/usr/bin/env python3
"""Setup script for the lambda_deploy package."""

from setuptools import setup, find_packages
from lambda_deploy import __version__

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="lambda_deploy_cli",
    version=__version__,
    description="A cli for deploying AWS Lambda functions",
    author="Povio",
    author_email="goran.parapid@povio.com",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'lambda-deploy=lambda_deploy.cli:cli',
        ],
    },
    install_requires=requirements,
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
