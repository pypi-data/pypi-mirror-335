#!/usr/bin/env python3
"""Tests for the configuration processor."""

import unittest
import os
import tempfile
import yaml
import json
from unittest.mock import patch, MagicMock

from lambda_deploy.utils.config_processor import (
    resolve_func_variables,
    resolve_env_variables,
    process_template_value,
    load_template,
    process_configs
)


class TestConfigProcessor(unittest.TestCase):
    """Test cases for the configuration processor."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()

        # Set the working directory to the temp directory
        self.original_dir = os.getcwd()
        os.chdir(self.temp_dir.name)

        # Create a template file
        os.makedirs(os.path.join(self.temp_dir.name, ".config"))
        self.template_file = os.path.join(self.temp_dir.name, ".config", "test.template.yml")
        with open(self.template_file, "w") as f:
            f.write("""
foo:
  stage: ${func:stage}
  release: ${func:release}
  api_key: "test-api-key"
  url: '${env:URL}'

http:
  log: true
  port: 3000
  service: "test-service"
""")

    def tearDown(self):
        """Tear down test fixtures."""
        # Restore the working directory
        os.chdir(self.original_dir)

        # Clean up the temporary directory
        self.temp_dir.cleanup()

    def test_resolve_func_variables(self):
        """Test resolving function variables."""
        # Test with stage only
        value = "${func:stage}-app"
        result = resolve_func_variables(value, "test", None)
        self.assertEqual(result, "test-app")

        # Test with stage and release
        value = "${func:stage}-${func:release}"
        result = resolve_func_variables(value, "test", "abc123")
        self.assertEqual(result, "test-abc123")

    def test_resolve_env_variables(self):
        """Test resolving environment variables."""
        # Set environment variable
        os.environ["TEST_ENV_VAR"] = "test_value"

        # Test with environment variable - should not be resolved
        value = "prefix-${TEST_ENV_VAR}-suffix"
        result = resolve_env_variables(value)
        self.assertEqual(result, "prefix-${TEST_ENV_VAR}-suffix")

        # Test with missing environment variable
        value = "prefix-${MISSING_ENV_VAR}-suffix"
        result = resolve_env_variables(value)
        self.assertEqual(result, "prefix-${MISSING_ENV_VAR}-suffix")

        # Test with env: prefix - should be resolved
        value = "prefix-${env:TEST_ENV_VAR}-suffix"
        result = resolve_env_variables(value)
        self.assertEqual(result, "prefix-test_value-suffix")

        # Test with missing env: prefix
        value = "prefix-${env:MISSING_ENV_VAR}-suffix"
        result = resolve_env_variables(value)
        self.assertEqual(result, "prefix-${env:MISSING_ENV_VAR}-suffix")

    def test_process_template_value(self):
        """Test processing template values."""
        # Test with string
        value = "${func:stage}-${env:TEST_ENV_VAR}"
        os.environ["TEST_ENV_VAR"] = "test_value"
        result = process_template_value(value, "test", "us-east-1", "abc123")
        self.assertEqual(result, "test-test_value")

        # Test with standard env var - should not be resolved
        value = "${func:stage}-${TEST_ENV_VAR}"
        result = process_template_value(value, "test", "us-east-1", "abc123")
        self.assertEqual(result, "test-${TEST_ENV_VAR}")

        # Test with dictionary
        value = {
            "stage": "${func:stage}",
            "env": "${env:TEST_ENV_VAR}",
            "standard_env": "${TEST_ENV_VAR}",
            "nested": {
                "release": "${func:release}"
            }
        }
        result = process_template_value(value, "test", "us-east-1", "abc123")
        self.assertEqual(result, {
            "stage": "test",
            "env": "test_value",
            "standard_env": "${TEST_ENV_VAR}",
            "nested": {
                "release": "abc123"
            }
        })

    def test_load_template(self):
        """Test loading and processing a template."""
        # Set environment variable
        os.environ["URL"] = "https://example.com"

        # Load template
        result = load_template(self.template_file, "test", "us-east-1", "abc123")

        # Check result
        self.assertEqual(result["foo"]["stage"], "test")
        self.assertEqual(result["foo"]["release"], "abc123")
        self.assertEqual(result["foo"]["api_key"], "test-api-key")
        self.assertEqual(result["foo"]["url"], "https://example.com")
        self.assertEqual(result["http"]["log"], True)
        self.assertEqual(result["http"]["port"], 3000)
        self.assertEqual(result["http"]["service"], "test-service")

    def test_process_configs(self):
        """Test processing configs section."""
        # Create a configuration
        config = {
            "region": "us-east-1",
            "configs": {
                "destination": "config.yml",
                "json": False,
                "values": [
                    {
                        "name": "@",
                        "configFrom": "template"
                    }
                ]
            }
        }

        # Set environment variable
        os.environ["URL"] = "https://example.com"

        # Process configs
        process_configs(config, "test", ".config", "abc123")

        # Check that the destination file was created
        self.assertTrue(os.path.exists("config.yml"))

        # Check the contents of the destination file
        with open("config.yml", "r") as f:
            result = yaml.safe_load(f)

        self.assertEqual(result["foo"]["stage"], "test")
        self.assertEqual(result["foo"]["release"], "abc123")
        self.assertEqual(result["foo"]["url"], "https://example.com")

    def test_process_configs_json_output(self):
        """Test processing configs section with JSON output."""
        # Create a configuration
        config = {
            "region": "us-east-1",
            "configs": {
                "destination": "config.json",
                "json": True,
                "values": [
                    {
                        "name": "@",
                        "configFrom": "template"
                    }
                ]
            }
        }

        # Set environment variable
        os.environ["URL"] = "https://example.com"

        # Process configs
        process_configs(config, "test", ".config", "abc123")

        # Check that the destination file was created
        self.assertTrue(os.path.exists("config.json"))

        # Check the contents of the destination file
        with open("config.json", "r") as f:
            result = json.load(f)

        self.assertEqual(result["foo"]["stage"], "test")
        self.assertEqual(result["foo"]["release"], "abc123")
        self.assertEqual(result["foo"]["url"], "https://example.com")

    def test_process_configs_custom_name(self):
        """Test processing configs section with custom name."""
        # Create a template file with custom name
        custom_template_file = os.path.join(self.temp_dir.name, ".config", "custom.template.yml")
        with open(custom_template_file, "w") as f:
            f.write("""
custom:
  value: ${func:stage}
""")

        # Create a configuration
        config = {
            "region": "us-east-1",
            "configs": {
                "destination": "custom-config.yml",
                "json": False,
                "values": [
                    {
                        "name": "custom",
                        "configFrom": "template"
                    }
                ]
            }
        }

        # Process configs
        process_configs(config, "test", ".config", "abc123")

        # Check that the destination file was created
        self.assertTrue(os.path.exists("custom-config.yml"))

        # Check the contents of the destination file
        with open("custom-config.yml", "r") as f:
            result = yaml.safe_load(f)

        self.assertEqual(result["custom"]["value"], "test")


if __name__ == "__main__":
    unittest.main()
