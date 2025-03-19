#!/usr/bin/env python3
"""Lambda Deployer for AWS Lambda functions."""

import os
import sys
import json
import time
import yaml
import boto3
import zipfile
import io
from typing import Dict, Any, Optional, List
from collections import OrderedDict

from lambda_deploy.utils.logging import log, debug, section, colorize, success, error, warning
from lambda_deploy.utils.config_processor import process_configs, OrderedLoader, get_aws_clients


class LambdaDeployer:
    """Handles AWS Lambda function deployment."""

    def __init__(self, stage: str, source_dir: Optional[str] = None, env_vars_path: Optional[str] = None,
                 config_dir: str = '.config', release: Optional[str] = None, skip_validation: bool = False):
        self.stage = stage
        self.config_dir = config_dir
        self.config_file = self._find_config_file(config_dir, stage)
        self.source_dir = source_dir
        self.env_vars_path = env_vars_path
        self.release = release
        self.skip_validation = skip_validation
        self.config = self._load_config()

        # validate AWS credentials
        if not self.skip_validation:
            self._validate_aws_credentials()

        # initialize AWS clients
        self.ssm, self.secretsmanager, self.lambda_client = get_aws_clients(
            region=self.config.get('region', 'us-east-1')
        )

    def _find_config_file(self, config_dir: str, stage: str) -> str:
        """find config file for stage"""
        # try different extensions
        for ext in ['yaml', 'yml']:
            file_path = f"{config_dir}/{stage}.lambda-deploy.{ext}"
            if os.path.exists(file_path):
                return file_path

        # default to yaml
        return f"{config_dir}/{stage}.lambda-deploy.yaml"

    def _validate_aws_credentials(self) -> None:
        """validate AWS credentials match account ID"""
        if 'accountId' not in self.config:
            warning("No accountId specified in configuration. Skipping credentials validation.")
            return

        expected_account_id = self.config['accountId']
        try:
            sts = boto3.client('sts', region_name=self.config.get('region', 'us-east-1'))
            identity = sts.get_caller_identity()
            current_account_id = identity['Account']

            if current_account_id != expected_account_id:
                error(f"AWS credentials are for account {current_account_id}, but config specifies account {expected_account_id}.")
                log("Please use the correct AWS credentials for this deployment.", color="RED")
                sys.exit(1)

            success(f"AWS credentials validated for account {current_account_id}")
        except Exception as e:
            error(f"Error validating AWS credentials: {e}")
            sys.exit(1)

    def _load_config(self) -> Dict[str, Any]:
        """load config from YAML file"""
        try:
            with open(self.config_file, 'r') as f:
                return yaml.load(f, Loader=OrderedLoader) or OrderedDict()
        except FileNotFoundError:
            error(f"Configuration file '{self.config_file}' not found.")
            sys.exit(1)
        except yaml.YAMLError as e:
            error(f"Error parsing YAML file: {e}")
            sys.exit(1)

    def _process_config_templates(self) -> None:
        """process config templates if present"""
        process_configs(self.config, self.stage, self.config_dir, self.release)

    def bootstrap(self) -> None:
        """bootstrap config templates"""
        self._process_config_templates()

    def _wait_for_lambda_update(self, function_name: str) -> bool:

        log("Waiting for update to complete...", color="BLUE")

        # display spinner
        spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        spinner_idx = 0
        start_time = time.time()

        while True:
            response = self.lambda_client.get_function(FunctionName=function_name)
            status = response['Configuration'].get('LastUpdateStatus')

            elapsed = time.time() - start_time
            spinner_char = spinner[spinner_idx % len(spinner)]
            spinner_idx += 1

            # clear line and update status
            sys.stdout.write('\r' + ' ' * 80)  # clear line
            sys.stdout.write(f"\r{colorize(spinner_char, 'BRIGHT_CYAN')} Status: {colorize(status or 'Updating', 'BRIGHT_YELLOW')} (elapsed: {elapsed:.1f}s)")
            sys.stdout.flush()

            if status == "Successful":
                sys.stdout.write('\n')  # move to next line
                success("Update completed successfully")
                return True
            elif status == "Failed":
                sys.stdout.write('\n')  # move to next line
                error("Update failed")
                return False

            time.sleep(0.5)

    def _create_zip_from_directory(self, directory: str) -> Optional[bytes]:
        """create zip file from directory"""
        if not os.path.exists(directory) or not os.path.isdir(directory):
            error(f"Directory '{directory}' not found or is not a directory.")
            return None

        log(f"Creating ZIP file from contents of '{directory}/' directory...")

        # check if directory is empty
        has_files = False
        for root, _, files in os.walk(directory):
            if files:
                has_files = True
                break

        if not has_files:
            error(f"Directory '{directory}' is empty. Cannot create a ZIP file from an empty directory.")
            return None

        # create archive
        zip_buffer = io.BytesIO()
        try:
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                file_count = 0
                for root, _, files in os.walk(directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # calculate archive path
                        archive_path = os.path.relpath(file_path, directory)
                        # add file to zip
                        zip_file.write(file_path, archive_path)
                        debug(f"Added {archive_path} to ZIP")
                        file_count += 1

                log(f"Added {colorize(str(file_count), 'BRIGHT_GREEN')} files to ZIP archive")

                if file_count == 0:
                    error("No files were added to the ZIP archive.")
                    return None
        except Exception as e:
            error(f"Error creating ZIP file: {e}")
            return None

        zip_buffer.seek(0)
        zip_data = zip_buffer.getvalue()

        # check if ZIP is empty
        if len(zip_data) <= 22:  # minimum size of valid ZIP
            error("Generated ZIP file is empty or invalid.")
            return None

        return zip_data

    def deploy(self, skip_env_update: bool = False) -> None:
        """deploy lambda function to AWS"""

        function_name = self.config.get('function-name')
        if not function_name:
            error("function-name not specified in configuration.")
            sys.exit(1)

        print("\n" + "=" * 80)
        log(f"Deploying Lambda Function: {colorize(function_name, 'BOLD')}", prefix="")
        print("=" * 80 + "\n")

        # check environment variables file, skip config update if not specified
        env_vars = {}
        if not skip_env_update:
            # If env_vars_path is not provided, check for {stage}-vars.json in current directory
            if not self.env_vars_path:
                # Check for {stage}-vars.json in current directory first
                stage_vars_file = f"{self.stage}-vars.json"
                if os.path.exists(stage_vars_file):
                    self.env_vars_path = stage_vars_file
                    log(f"Found stage variables file: {colorize(stage_vars_file, 'BRIGHT_GREEN')}")

            if self.env_vars_path and os.path.exists(self.env_vars_path):
                try:
                    with open(self.env_vars_path, 'r') as f:
                        env_vars = json.load(f)
                    log(f"Loaded environment variables from {colorize(self.env_vars_path, 'BRIGHT_GREEN')}")
                except Exception as e:
                    error(f"Error loading environment variables from {self.env_vars_path}: {e}")
                    sys.exit(1)
            else:
                warning("No environment variables file specified or found, skipping environment variable update")
                skip_env_update = True

            if env_vars and not skip_env_update:
                log("Updating Lambda configuration...", color="BLUE")
                try:
                    self.lambda_client.update_function_configuration(
                        FunctionName=function_name,
                        Environment={'Variables': env_vars}
                    )

                    if not self._wait_for_lambda_update(function_name):
                        error("Failed to update Lambda configuration.")
                        sys.exit(1)
                except Exception as e:
                    error(f"Error updating Lambda configuration: {e}")
                    sys.exit(1)
        else:
            log("Skipping environment variable update", color="YELLOW")

        zip_content = None

        if self.source_dir:
            log(f"Using source directory specified by --source: {colorize(self.source_dir, 'BRIGHT_GREEN')}")
            # check source directory
            if not os.path.exists(self.source_dir) or not os.path.isdir(self.source_dir):
                error(f"Source directory '{self.source_dir}' does not exist or is not a directory.")
                log("Please make sure the directory exists before deploying.", color="RED")
                sys.exit(1)

            zip_content = self._create_zip_from_directory(self.source_dir)
            if not zip_content:
                error(f"Failed to create ZIP file from source directory: {self.source_dir}")
                sys.exit(1)
        else:
            # use build-dir from config
            dist_dir = self.config.get('build-dir') or self.config.get('dist-dir', 'dist')
            log(f"No source directory specified. Using default: {colorize(dist_dir, 'BRIGHT_GREEN')}")

            # check directory
            if not os.path.exists(dist_dir) or not os.path.isdir(dist_dir):
                error(f"Directory '{dist_dir}' does not exist or is not a directory.")
                log("Please make sure the directory exists before deploying.", color="RED")
                log("You can specify a different directory using the --source option.", color="YELLOW")
                sys.exit(1)

            zip_content = self._create_zip_from_directory(dist_dir)
            if not zip_content:
                error(f"Failed to create ZIP file from default directory: {dist_dir}")
                sys.exit(1)

        # update Lambda code
        if zip_content:
            log("Updating Lambda function code...", color="BLUE")
            try:
                self.lambda_client.update_function_code(
                    FunctionName=function_name,
                    ZipFile=zip_content
                )

                if not self._wait_for_lambda_update(function_name):
                    error("Failed to update Lambda code.")
                    sys.exit(1)
            except Exception as e:
                error(f"Error updating Lambda code: {e}")
                sys.exit(1)

        success("Lambda update completed successfully!")
        print("\n" + "=" * 80 + "\n")
        self.show_info()

    def show_info(self) -> None:
        """display lambda function configuration"""
        function_name = self.config.get('function-name')
        if not function_name:
            log("Error: function-name not specified in configuration.", color="RED", error=True)
            sys.exit(1)

        # display header
        print("\n" + "=" * 80)
        log(f"Lambda Function: {colorize(function_name, 'BOLD')}", prefix="")
        print("=" * 80)

        # basic info section
        section("Basic Information")
        log(f"Stage: {colorize(self.stage, 'BRIGHT_GREEN')}")
        log(f"Region: {colorize(self.config.get('region', 'us-east-1'), 'BRIGHT_GREEN')}")
        log(f"Account ID: {colorize(self.config.get('accountId', 'Not specified'), 'BRIGHT_GREEN')}")
        log(f"Configuration file: {colorize(self.config_file, 'BRIGHT_GREEN')}")

        # display config templates
        if 'configs' in self.config:
            section("Configuration Templates")
            configs = self.config['configs']

            # handle list format
            if isinstance(configs, list):
                log(f"Number of configurations: {colorize(str(len(configs)), 'BRIGHT_GREEN')}")

                for i, config_item in enumerate(configs):
                    if isinstance(config_item, dict):
                        print("")
                        log(f"Configuration #{colorize(str(i+1), 'BOLD')}")
                        log(f"  Destination: {colorize(config_item.get('destination', 'Not specified'), 'BRIGHT_GREEN')}")
                        log(f"  Output as JSON: {colorize(str(config_item.get('json', False)), 'BRIGHT_GREEN')}")

                        if 'values' in config_item and isinstance(config_item['values'], list):
                            log("  Template Values:")
                            for value in config_item['values']:
                                if isinstance(value, dict):
                                    name = value.get('name', 'Not specified')
                                    config_from = value.get('configFrom', 'Not specified')
                                    log(f"    • {colorize(name, 'BRIGHT_YELLOW')} from {colorize(config_from, 'BRIGHT_BLUE')}")
            # handle dict format
            elif isinstance(configs, dict):
                log(f"Destination: {colorize(configs.get('destination', 'Not specified'), 'BRIGHT_GREEN')}")
                log(f"Output as JSON: {colorize(str(configs.get('json', False)), 'BRIGHT_GREEN')}")

                if 'values' in configs and isinstance(configs['values'], list):
                    log("Template Values:")
                    for value in configs['values']:
                        if isinstance(value, dict):
                            name = value.get('name', 'Not specified')
                            config_from = value.get('configFrom', 'Not specified')
                            log(f"  • {colorize(name, 'BRIGHT_YELLOW')} from {colorize(config_from, 'BRIGHT_BLUE')}")

        # display environment variables
        section("Environment Variables")

        # Check for {stage}-vars.json in current directory first
        stage_vars_file = f"{self.stage}-vars.json"
        if os.path.exists(stage_vars_file):
            env_vars_file = stage_vars_file
        # Then check in config directory
        elif os.path.exists(f"{self.config_dir}/{self.stage}-vars.json"):
            env_vars_file = f"{self.config_dir}/{self.stage}-vars.json"
        else:
            env_vars_file = None

        if env_vars_file:
            log(f"Environment variables file: {colorize(env_vars_file, 'BRIGHT_GREEN')}")
            try:
                with open(env_vars_file, 'r') as f:
                    env_vars = json.load(f)
                log(f"Number of variables: {colorize(str(len(env_vars)), 'BRIGHT_GREEN')}")
            except Exception as e:
                log(f"Error reading environment variables file: {e}", color="YELLOW")
        else:
            log("No environment variables file found", color="YELLOW")

        # get Lambda function info
        try:
            section("Lambda Function Details")
            response = self.lambda_client.get_function(FunctionName=function_name)
            config = response['Configuration']

            log(f"Runtime: {colorize(config.get('Runtime', 'Unknown'), 'BRIGHT_GREEN')}")
            log(f"Handler: {colorize(config.get('Handler', 'Unknown'), 'BRIGHT_GREEN')}")
            log(f"Memory Size: {colorize(str(config.get('MemorySize', 'Unknown')), 'BRIGHT_GREEN')} MB")
            log(f"Timeout: {colorize(str(config.get('Timeout', 'Unknown')), 'BRIGHT_GREEN')} seconds")
            log(f"Last Modified: {colorize(config.get('LastModified', 'Unknown'), 'BRIGHT_GREEN')}")

            # show current env vars
            if 'Environment' in config and 'Variables' in config['Environment']:
                section("Current Environment Variables")
                for key, value in config['Environment']['Variables'].items():
                    log(f"{colorize(key, 'BRIGHT_YELLOW')}: {colorize('[MASKED]', 'BRIGHT_RED')}")

            print("\n" + "=" * 80 + "\n")

        except Exception as e:
            section("Lambda Function Status")
            log(f"Could not retrieve Lambda function details: {e}", color="YELLOW")
            log("The function may not exist yet or you may not have permission to access it.", color="YELLOW")
            print("\n" + "=" * 80 + "\n")
