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

        # Create template files
        os.makedirs(os.path.join(self.temp_dir.name, ".config"))

        # Main template
        self.template_file = os.path.join(self.temp_dir.name, ".config", "test.template.yml")
        with open(self.template_file, "w") as f:
            f.write("""
logging:
  level: info
  format: json

core:
  stage: ${func:stage}
  release: ${func:release}

database:
  username: ${env:DB_USERNAME}
  password: ${arn:aws:secretsmanager:us-east-1:123456789012:secret:myapp-dev/lambda/darabase-XXXXXX::password}
  database: ${arn:aws:ssm:us-east-1:123456789012:parameter/myapp-dev/lambda/database/db-name}
""")

        # Environment template
        self.env_template_file = os.path.join(self.temp_dir.name, ".config", "test.env.template.yml")
        with open(self.env_template_file, "w") as f:
            f.write("""
username: ${env:DB_USERNAME}
password: ${arn:aws:secretsmanager:us-east-1:123456789012:secret:dev/lambda/database-XXXXXX::password}
database: ${arn:aws:ssm:us-east-1:123456789012:parameter/dev/lambda/database/database-name}
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

        # Test with environment variable - should be resolved
        value = "prefix-${env:TEST_ENV_VAR}-suffix"
        result = resolve_env_variables(value)
        self.assertEqual(result, "prefix-test_value-suffix")

        # Test with missing environment variable - should resolve to empty string
        value = "prefix-${env:MISSING_ENV_VAR}-suffix"
        result = resolve_env_variables(value)
        self.assertEqual(result, "prefix--suffix")

        # Test with multiple environment variables
        value = "${env:TEST_ENV_VAR}-${env:MISSING_ENV_VAR}-${env:TEST_ENV_VAR}"
        result = resolve_env_variables(value)
        self.assertEqual(result, "test_value--test_value")

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
        os.environ["DB_USERNAME"] = "test-user"

        # Mock AWS responses
        mock_ssm_response = {
            'Parameter': {
                'Value': 'test-db-name'
            }
        }
        mock_secret_response = {
            'SecretString': json.dumps({
                'password': 'test-password'
            })
        }

        with patch('lambda_deploy.utils.config_processor.get_aws_clients') as mock_get_clients:
            # Setup mock clients
            mock_ssm = MagicMock()
            mock_ssm.get_parameter.return_value = mock_ssm_response
            mock_secretsmanager = MagicMock()
            mock_secretsmanager.get_secret_value.return_value = mock_secret_response
            mock_get_clients.return_value = (mock_ssm, mock_secretsmanager, None)

            # Load template
            result = load_template(self.template_file, "test", "us-east-1", "abc123")

            # Check result
            self.assertEqual(result["logging"]["level"], "info")
            self.assertEqual(result["logging"]["format"], "json")
            self.assertEqual(result["core"]["stage"], "test")
            self.assertEqual(result["core"]["release"], "abc123")
            self.assertEqual(result["database"]["username"], "test-user")
            self.assertEqual(result["database"]["password"], "test-password")
            self.assertEqual(result["database"]["database"], "test-db-name")

    def test_process_configs(self):
        """Test processing configs section."""
        # Create a configuration
        config = {
            "region": "us-east-1",
            "configs": {
                "destination": "config.yml",
                "values": [
                    {
                        "name": "@",
                        "configFrom": "template"
                    }
                ]
            }
        }

        # Set environment variable
        os.environ["DB_USERNAME"] = "test-user"

        # Mock AWS responses
        mock_ssm_response = {
            'Parameter': {
                'Value': 'test-db-name'
            }
        }
        mock_secret_response = {
            'SecretString': json.dumps({
                'password': 'test-password'
            })
        }

        with patch('lambda_deploy.utils.config_processor.get_aws_clients') as mock_get_clients:
            # Setup mock clients
            mock_ssm = MagicMock()
            mock_ssm.get_parameter.return_value = mock_ssm_response
            mock_secretsmanager = MagicMock()
            mock_secretsmanager.get_secret_value.return_value = mock_secret_response
            mock_get_clients.return_value = (mock_ssm, mock_secretsmanager, None)

            # Process configs
            process_configs(config, "test", ".config", "abc123")

            # Check that the destination file was created
            self.assertTrue(os.path.exists("config.yml"))

            # Check the contents of the destination file
            with open("config.yml", "r") as f:
                result = yaml.safe_load(f)

            self.assertEqual(result["logging"]["level"], "info")
            self.assertEqual(result["logging"]["format"], "json")
            self.assertEqual(result["core"]["stage"], "test")
            self.assertEqual(result["core"]["release"], "abc123")
            self.assertEqual(result["database"]["username"], "test-user")
            self.assertEqual(result["database"]["password"], "test-password")
            self.assertEqual(result["database"]["database"], "test-db-name")

    def test_process_configs_json_output(self):
        """Test processing configs section with JSON output."""
        # Create a configuration
        config = {
            "region": "us-east-1",
            "configs": {
                "destination": "config.json",
                "values": [
                    {
                        "name": "@",
                        "configFrom": "template"
                    }
                ]
            }
        }

        # Set environment variable
        os.environ["DB_USERNAME"] = "test-user"

        # Mock AWS responses
        mock_ssm_response = {
            'Parameter': {
                'Value': 'test-db-name'
            }
        }
        mock_secret_response = {
            'SecretString': json.dumps({
                'password': 'test-password'
            })
        }

        with patch('lambda_deploy.utils.config_processor.get_aws_clients') as mock_get_clients:
            # Setup mock clients
            mock_ssm = MagicMock()
            mock_ssm.get_parameter.return_value = mock_ssm_response
            mock_secretsmanager = MagicMock()
            mock_secretsmanager.get_secret_value.return_value = mock_secret_response
            mock_get_clients.return_value = (mock_ssm, mock_secretsmanager, None)

            # Process configs
            process_configs(config, "test", ".config", "abc123")

            # Check that the destination file was created
            self.assertTrue(os.path.exists("config.json"))

            # Check the contents of the destination file
            with open("config.json", "r") as f:
                result = json.load(f)

            self.assertEqual(result["logging"]["level"], "info")
            self.assertEqual(result["logging"]["format"], "json")
            self.assertEqual(result["core"]["stage"], "test")
            self.assertEqual(result["core"]["release"], "abc123")
            self.assertEqual(result["database"]["username"], "test-user")
            self.assertEqual(result["database"]["password"], "test-password")
            self.assertEqual(result["database"]["database"], "test-db-name")

    def test_process_configs_env_output(self):
        """Test processing configs section with ENV output."""
        # Create a configuration
        config = {
            "region": "us-east-1",
            "configs": {
                "destination": "config.env",
                "values": [
                    {
                        "name": "@",
                        "configFrom": "template"
                    }
                ]
            }
        }

        # Set environment variable
        os.environ["DB_USERNAME"] = "test-user"

        # Mock AWS responses
        mock_ssm_response = {
            'Parameter': {
                'Value': 'test-db-name'
            }
        }
        mock_secret_response = {
            'SecretString': json.dumps({
                'password': 'test-password'
            })
        }

        with patch('lambda_deploy.utils.config_processor.get_aws_clients') as mock_get_clients:
            # Setup mock clients
            mock_ssm = MagicMock()
            mock_ssm.get_parameter.return_value = mock_ssm_response
            mock_secretsmanager = MagicMock()
            mock_secretsmanager.get_secret_value.return_value = mock_secret_response
            mock_get_clients.return_value = (mock_ssm, mock_secretsmanager, None)

            # Process configs
            process_configs(config, "test", ".config", "abc123")

            # Check that the destination file was created
            self.assertTrue(os.path.exists("config.env"))

            # Check the contents of the destination file
            with open("config.env", "r") as f:
                lines = f.readlines()
                env_vars = {}
                for line in lines:
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value

            self.assertEqual(env_vars["logging_level"], "info")
            self.assertEqual(env_vars["logging_format"], "json")
            self.assertEqual(env_vars["core_stage"], "test")
            self.assertEqual(env_vars["core_release"], "abc123")
            self.assertEqual(env_vars["database_username"], "test-user")
            self.assertEqual(env_vars["database_password"], "test-password")
            self.assertEqual(env_vars["database_database"], "test-db-name")

    def test_process_configs_multiple_destinations(self):
        """Test processing configs section with multiple destinations."""
        # Create a configuration
        config = {
            "region": "us-east-1",
            "configs": [
                {
                    "destination": "./dist/config.yml",
                    "values": [
                        {
                            "name": "@",
                            "configFrom": "template"
                        }
                    ]
                },
                {
                    "destination": "test-vars.json",
                    "values": [
                        {
                            "name": "@",
                            "configFrom": "env.template"
                        }
                    ]
                }
            ]
        }

        # Set environment variable
        os.environ["DB_USERNAME"] = "test-user"

        # Mock AWS responses
        mock_ssm_response = {
            'Parameter': {
                'Value': 'test-db-name'
            }
        }
        mock_secret_response = {
            'SecretString': json.dumps({
                'password': 'test-password'
            })
        }

        with patch('lambda_deploy.utils.config_processor.get_aws_clients') as mock_get_clients:
            # Setup mock clients
            mock_ssm = MagicMock()
            mock_ssm.get_parameter.return_value = mock_ssm_response
            mock_secretsmanager = MagicMock()
            mock_secretsmanager.get_secret_value.return_value = mock_secret_response
            mock_get_clients.return_value = (mock_ssm, mock_secretsmanager, None)

            # Create dist directory
            os.makedirs("dist", exist_ok=True)

            # Process configs
            process_configs(config, "test", ".config", "abc123")

            # Check that both destination files were created
            self.assertTrue(os.path.exists("./dist/config.yml"))
            self.assertTrue(os.path.exists("test-vars.json"))

            # Check the contents of the config file
            with open("./dist/config.yml", "r") as f:
                result = yaml.safe_load(f)

            self.assertEqual(result["logging"]["level"], "info")
            self.assertEqual(result["logging"]["format"], "json")
            self.assertEqual(result["core"]["stage"], "test")
            self.assertEqual(result["core"]["release"], "abc123")
            self.assertEqual(result["database"]["username"], "test-user")
            self.assertEqual(result["database"]["password"], "test-password")
            self.assertEqual(result["database"]["database"], "test-db-name")

            # Check the contents of the env vars file
            with open("test-vars.json", "r") as f:
                result = json.load(f)

            self.assertEqual(result["username"], "test-user")
            self.assertEqual(result["password"], "test-password")
            self.assertEqual(result["database"], "test-db-name")


if __name__ == "__main__":
    unittest.main()
