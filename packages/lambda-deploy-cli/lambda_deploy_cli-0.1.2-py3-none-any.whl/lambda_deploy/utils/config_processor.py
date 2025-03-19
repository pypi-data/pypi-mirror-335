#!/usr/bin/env python3
"""Config processor for Lambda deployment."""

import os
import re
import json
import yaml
import subprocess
import boto3
from typing import Dict, Any, Optional, List, Union
from collections import OrderedDict

from lambda_deploy.utils.logging import log, debug


def get_git_commit_hash() -> str:
    """Get git commit hash.

    Returns:
        Git commit hash or 'unknown'
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        return "unknown"


def resolve_func_variables(value: str, stage: str, release: Optional[str] = None, local_vars: Optional[Dict[str, str]] = None) -> str:
    """Resolve function variables.

    Args:
        value: String with function variables
        stage: Deployment stage
        release: Release identifier
        local_vars: Local variables dictionary

    Returns:
        String with resolved variables
    """
    if release is None:
        release = os.environ.get('RELEASE', get_git_commit_hash())

    # replace ${func:stage} with stage
    value = value.replace('${func:stage}', stage)

    # replace ${func:release} with release
    value = value.replace('${func:release}', release)

    # replace other ${func:variable} with values from local_vars
    if local_vars:
        func_var_pattern = r'\${func:([A-Za-z0-9_]+)}'
        matches = re.findall(func_var_pattern, value)

        for match in matches:
            if match in local_vars:
                value = value.replace(f'${{func:{match}}}', str(local_vars[match]))

    return value


def resolve_env_variables(value: str) -> str:
    """Resolve environment variables.

    Args:
        value: String with environment variables

    Returns:
        String with resolved variables
    """
    # Handle ${env:VAR_NAME} pattern
    env_prefix_pattern = r'\${env:([A-Za-z0-9_]+)}'
    env_prefix_matches = re.findall(env_prefix_pattern, value)

    # Replace each ${env:VAR_NAME} with env var value
    for match in env_prefix_matches:
        placeholder = f'${{env:{match}}}'
        env_value = os.environ.get(match)
        if env_value is not None:
            value = value.replace(placeholder, env_value)

    return value


def _resolve_parameter_store(param_path: str, region: str) -> str:
    """Get value from Parameter Store.

    Args:
        param_path: Parameter path
        region: AWS region

    Returns:
        Parameter value or empty string
    """
    try:
        ssm = boto3.client('ssm', region_name=region)
        response = ssm.get_parameter(Name=param_path, WithDecryption=True)
        return response['Parameter']['Value']
    except Exception as e:
        log(f"Error retrieving parameter {param_path}: {e}")
        return ""


def _resolve_secrets_manager(secret_id: str, region: str) -> str:
    """Get value from Secrets Manager.

    Args:
        secret_id: Secret ID
        region: AWS region

    Returns:
        Secret value or empty string
    """
    # check for specific key
    key = None
    if '::' in secret_id:
        secret_id, key = secret_id.split('::', 1)
    try:
        secretsmanager = boto3.client('secretsmanager', region_name=region)
        response = secretsmanager.get_secret_value(SecretId=secret_id)
        secret_string = response['SecretString']

        if key:
            try:
                secret_json = json.loads(secret_string)
                if isinstance(secret_json, dict) and key in secret_json:
                    return str(secret_json[key])
                else:
                    log(f"Warning: Key '{key}' not found in secret JSON or secret is not a JSON object")
                    return ""
            except json.JSONDecodeError:
                log(f"Warning: Secret is not valid JSON, cannot extract key '{key}'")
                return ""

        return secret_string
    except Exception as e:
        log(f"Error retrieving secret {secret_id}: {e}")
        return ""


def resolve_aws_references(value: str, region: str) -> str:
    """Resolve AWS resource references.

    Args:
        value: String with AWS references
        region: AWS region

    Returns:
        String with resolved references
    """
    # check for parameter store reference
    if value.startswith("arn:aws:ssm:"):
        param_path = value
        # extract parameter path from ARN
        parts = value.split(":", 6)
        if len(parts) >= 7:
            param_path = parts[6]
        return _resolve_parameter_store(param_path, region)

    # check for secrets manager reference
    if value.startswith("arn:aws:secretsmanager:"):
        return _resolve_secrets_manager(value, region)

    return value


def process_template_value(value: Any, stage: str, region: str = "us-east-1", release: Optional[str] = None, local_vars: Optional[Dict[str, str]] = None) -> Any:
    """Process template value.

    Args:
        value: Value to process
        stage: Deployment stage
        region: AWS region
        release: Release identifier
        local_vars: Local variables dictionary

    Returns:
        Processed value
    """
    if isinstance(value, str):
        # process function variables
        value = resolve_func_variables(value, stage, release, local_vars)

        # process environment variables
        value = resolve_env_variables(value)

        # process AWS resource references
        if value.startswith("arn:aws:"):
            value = resolve_aws_references(value, region)

        return value
    elif isinstance(value, dict):
        # create new OrderedDict with same order
        result = OrderedDict()
        for k, v in value.items():
            result[k] = process_template_value(v, stage, region, release, local_vars)
        return result
    elif isinstance(value, list):
        return [process_template_value(item, stage, region, release, local_vars) for item in value]
    else:
        return value


# custom YAML loader to preserve order
class OrderedLoader(yaml.SafeLoader):
    pass


def construct_mapping(loader, node):
    loader.flatten_mapping(node)
    return OrderedDict(loader.construct_pairs(node))


OrderedLoader.add_constructor(
    yaml.resolver.Resolver.DEFAULT_MAPPING_TAG,
    construct_mapping
)


# custom YAML dumper to preserve order
class OrderedDumper(yaml.SafeDumper):
    pass


def represent_ordereddict(dumper, data):
    return dumper.represent_mapping(
        yaml.resolver.Resolver.DEFAULT_MAPPING_TAG,
        data.items()
    )


OrderedDumper.add_representer(OrderedDict, represent_ordereddict)
# ensure strings are not quoted unnecessarily
OrderedDumper.add_representer(str, lambda dumper, data: dumper.represent_scalar('tag:yaml.org,2002:str', data, style=None if '\n' in data else ''))


def load_template(template_path: str, stage: str, region: str = "us-east-1", release: Optional[str] = None, local_vars: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Load and process template file.

    Args:
        template_path: Template file path
        stage: Deployment stage
        region: AWS region
        release: Release identifier
        local_vars: Local variables dictionary

    Returns:
        Processed template dictionary
    """
    try:
        with open(template_path, 'r') as f:
            template_data = yaml.load(f, Loader=OrderedLoader)

        if template_data is None:
            template_data = OrderedDict()

        # process all values in template
        processed_data = process_template_value(template_data, stage, region, release, local_vars)

        return processed_data
    except FileNotFoundError:
        log(f"Error: Template file '{template_path}' not found.")
        return OrderedDict()
    except yaml.YAMLError as e:
        log(f"Error parsing YAML template file: {e}")
        return OrderedDict()


def process_configs(config: Dict[str, Any], stage: str, config_dir: str, release: Optional[str] = None) -> None:
    """Process configs section.

    Args:
        config: Configuration dictionary
        stage: Deployment stage
        config_dir: Config directory
        release: Release identifier
    """
    if 'configs' not in config:
        debug("No configs section found in configuration.")
        return

    configs = config['configs']

    # create local variables dictionary
    local_vars = {
        'stage': stage,
        'release': release or os.environ.get('RELEASE', get_git_commit_hash())
    }

    # add other useful variables from config
    for key, value in config.items():
        if isinstance(value, (str, int, float, bool)):
            local_vars[key] = value

    # check if configs is a dictionary with destination and values
    if isinstance(configs, dict) and 'destination' in configs and 'values' in configs:
        # process single config
        _process_single_config(configs, stage, config_dir, release, local_vars, config.get('region', 'us-east-1'))
    elif isinstance(configs, list):
        # process multiple configs
        for config_item in configs:
            if isinstance(config_item, dict) and 'destination' in config_item and 'values' in config_item:
                _process_single_config(config_item, stage, config_dir, release, local_vars, config.get('region', 'us-east-1'))
            else:
                log("Warning: Invalid config item in configs list. Skipping.")
    else:
        # handle backward compatibility
        try:
            # extract all configs from dictionary
            config_items = []
            current_config = {}

            for key, value in configs.items():
                if key == 'destination':
                    # if we already have a destination, this is a new config
                    if 'destination' in current_config:
                        config_items.append(current_config.copy())
                        current_config = {}
                    current_config['destination'] = value
                elif key == 'json':
                    current_config['json'] = value
                elif key == 'values':
                    current_config['values'] = value

            # add last config if it exists
            if current_config and 'destination' in current_config and 'values' in current_config:
                config_items.append(current_config)

            # process all configs
            for config_item in config_items:
                _process_single_config(config_item, stage, config_dir, release, local_vars, config.get('region', 'us-east-1'))
        except Exception as e:
            log(f"Error processing configs: {e}")
            log("Warning: configs section is not properly formatted. Skipping config processing.")


def _process_single_config(config_item: Dict[str, Any], stage: str, config_dir: str, release: Optional[str] = None,
                          local_vars: Optional[Dict[str, Any]] = None, region: str = 'us-east-1') -> None:
    """Process single config item.

    Args:
        config_item: Config item dictionary
        stage: Deployment stage
        config_dir: Config directory
        release: Release identifier
        local_vars: Local variables dictionary
        region: AWS region
    """
    destination = config_item.get('destination')
    if not destination:
        log("Warning: No destination specified in config item. Skipping.")
        return

    output_as_json = config_item.get('json', False)

    if 'values' not in config_item or not isinstance(config_item['values'], list):
        log("Warning: No values list found in config item. Skipping.")
        return

    # process each value
    for value_config in config_item['values']:
        if not isinstance(value_config, dict):
            continue

        name = value_config.get('name')
        config_from = value_config.get('configFrom')

        if not name or not config_from:
            continue

        # determine template file path
        template_path = None
        if name == '@':
            yml_path = os.path.join(config_dir, f"{stage}.{config_from}.yml")
            yaml_path = os.path.join(config_dir, f"{stage}.{config_from}.yaml")

            if os.path.exists(yml_path):
                template_path = yml_path
            elif os.path.exists(yaml_path):
                template_path = yaml_path
            else:
                log(f"Error: Template file for '{stage}.{config_from}' not found in {config_dir}.")
                log(f"Looked for: {yml_path} and {yaml_path}")
                continue
        else:
            yml_path = os.path.join(config_dir, f"{name}.{config_from}.yml")
            yaml_path = os.path.join(config_dir, f"{name}.{config_from}.yaml")

            if os.path.exists(yml_path):
                template_path = yml_path
            elif os.path.exists(yaml_path):
                template_path = yaml_path
            else:
                log(f"Error: Template file for '{name}.{config_from}' not found in {config_dir}.")
                log(f"Looked for: {yml_path} and {yaml_path}")
                continue

        # load and process template
        processed_data = load_template(template_path, stage, region, release, local_vars)

        if not processed_data:
            log(f"Warning: No data loaded from template '{template_path}'. Skipping.")
            continue

        # create output directory if needed
        try:
            os.makedirs(os.path.dirname(os.path.abspath(destination)), exist_ok=True)
        except Exception as e:
            log(f"Error creating directory for '{destination}': {e}")
            continue

        # write processed data to destination
        try:
            if output_as_json:
                with open(destination, 'w') as f:
                    json.dump(processed_data, f, indent=2)
                log(f"Generated JSON configuration file: {destination}")
            else:
                with open(destination, 'w') as f:
                    yaml.dump(processed_data, f, default_flow_style=False, Dumper=OrderedDumper, sort_keys=False)
                log(f"Generated YAML configuration file: {destination}")
        except Exception as e:
            log(f"Error writing configuration file '{destination}': {e}")
