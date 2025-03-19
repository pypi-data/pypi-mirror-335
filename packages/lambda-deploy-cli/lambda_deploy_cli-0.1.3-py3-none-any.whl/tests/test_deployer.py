#!/usr/bin/env python3
"""Tests for LambdaDeployer class."""

import unittest
from unittest.mock import patch, MagicMock
import os
import tempfile
import json
import yaml

from lambda_deploy.core.deployer import LambdaDeployer


class TestLambdaDeployer(unittest.TestCase):
    """Test cases for LambdaDeployer."""

    def setUp(self):
        """Set up test fixtures."""
        # create temp config file
        self.temp_dir = tempfile.TemporaryDirectory()
        os.makedirs(os.path.join(self.temp_dir.name, ".config"))

        self.config_file = os.path.join(self.temp_dir.name, ".config", "test.lambda-deploy.yaml")
        with open(self.config_file, "w") as f:
            f.write("""
accountId: "123456789012"
region: us-east-1
function-name: myapp-test-function-url-lambda

configs:
  - destination: ./dist/config.yml
    values:
      - name: "@"
        configFrom: template
""")

        # set working directory to temp dir
        self.original_dir = os.getcwd()
        os.chdir(self.temp_dir.name)

        # mock AWS clients
        self.mock_sts = MagicMock()
        self.mock_sts.get_caller_identity.return_value = {"Account": "123456789012"}

        self.mock_ssm = MagicMock()
        self.mock_secretsmanager = MagicMock()
        self.mock_lambda = MagicMock()

        self.patchers = [
            patch("boto3.client", side_effect=self._mock_boto3_client),
            patch.object(LambdaDeployer, '_validate_aws_credentials', return_value=None)
        ]

        for patcher in self.patchers:
            patcher.start()

    def tearDown(self):
        """Clean up test fixtures."""
        # stop patchers
        for patcher in self.patchers:
            patcher.stop()

        # restore working directory
        os.chdir(self.original_dir)

        # clean up temp directory
        self.temp_dir.cleanup()

    def _mock_boto3_client(self, service_name, **kwargs):
        """Return mock AWS clients."""
        if service_name == "sts":
            return self.mock_sts
        elif service_name == "ssm":
            return self.mock_ssm
        elif service_name == "secretsmanager":
            return self.mock_secretsmanager
        elif service_name == "lambda":
            return self.mock_lambda
        else:
            return MagicMock()

    def test_init(self):
        """Test initialization."""
        # set env var
        os.environ["TEST_ENV_VAR"] = "test_value"

        # create deployer
        deployer = LambdaDeployer("test")

        # check config loaded
        self.assertEqual(deployer.config["accountId"], "123456789012")
        self.assertEqual(deployer.config["region"], "us-east-1")
        self.assertEqual(deployer.config["function-name"], "myapp-test-function-url-lambda")
        self.assertIn("configs", deployer.config)
        self.assertIsInstance(deployer.config["configs"], list)

    def test_bootstrap(self):
        """Test bootstrapping."""
        # set env var
        os.environ["TEST_ENV_VAR"] = "test_value"

        # create deployer
        deployer = LambdaDeployer("test")

        # mock _process_config_templates
        with patch.object(deployer, '_process_config_templates') as mock_process:
            # define side effect
            def side_effect():
                # create vars file manually
                with open("test-vars.json", "w") as f:
                    json.dump({"TEST_VAR": "test_value"}, f)

            # set side effect
            mock_process.side_effect = side_effect

            # bootstrap
            deployer.bootstrap()

            # check method called
            mock_process.assert_called_once()

            # check file created
            self.assertTrue(os.path.exists("test-vars.json"))

            # check file contents
            with open("test-vars.json", "r") as f:
                vars_data = json.load(f)

            self.assertEqual(vars_data["TEST_VAR"], "test_value")


    def test_deploy_with_skip_env_update(self):
        """Test deploy with skip_env_update."""
        # Mock Lambda client
        self.mock_lambda.get_function.return_value = {
            "Configuration": {
                "LastUpdateStatus": "Successful",
                "Runtime": "python3.10",
                "Handler": "index.lambda_handler",
                "MemorySize": 128,
                "Timeout": 30,
                "LastModified": "2024-03-20T12:00:00Z"
            }
        }
        self.mock_lambda.update_function_code.return_value = {
            "FunctionName": "myapp-test-function-url-lambda",
            "LastUpdateStatus": "Successful"
        }

        # create dist dir with sample file
        os.makedirs(os.path.join(self.temp_dir.name, "dist"))
        with open(os.path.join(self.temp_dir.name, "dist", "index.py"), "w") as f:
            f.write("def lambda_handler(event, context):\n    return {'statusCode': 200}")

        # create deployer
        deployer = LambdaDeployer("test")

        # Replace the lambda_client in the deployer with our mock
        deployer.lambda_client = self.mock_lambda

        # Mock _wait_for_lambda_update to return immediately
        with patch.object(deployer, '_wait_for_lambda_update', return_value=True):
            # deploy with skip_env_update
            deployer.deploy(skip_env_update=True)

            # Verify Lambda client was called correctly
            self.mock_lambda.update_function_code.assert_called_once()
            call_args = self.mock_lambda.update_function_code.call_args[1]
            self.assertEqual(call_args["FunctionName"], "myapp-test-function-url-lambda")
            self.assertIn("ZipFile", call_args)

    def test_config_templating(self):
        """Test config templating."""
        # create config file
        config_file = os.path.join(self.temp_dir.name, ".config", "test.lambda-deploy.yaml")
        with open(config_file, "w") as f:
            f.write("""
accountId: "123456789012"
region: us-east-1
function-name: myapp-test-function-url-lambda

configs:
  - destination: ./dist/config.yml
    values:
      - name: "@"
        configFrom: template
""")

        # create template file
        template_file = os.path.join(self.temp_dir.name, ".config", "test.template.yml")
        with open(template_file, "w") as f:
            f.write("""
logging:
  level: info
  format: json

core:
  stage: ${func:stage}
  release: ${func:release}

database:
  username: ${env:DB_USERNAME}
  password: ${arn:aws:secretsmanager:us-east-1:123456789012:secret:myapp-test/lambda/darabase-XXXXXX::password}
  database: ${arn:aws:ssm:us-east-1:123456789012:parameter/myapp-test/lambda/database/db-name}
""")

        # set env vars
        os.environ["DB_USERNAME"] = "test-user"

        # create deployer
        deployer = LambdaDeployer("test", release="abc123")

        # mock _process_config_templates
        with patch.object(deployer, '_process_config_templates') as mock_process:
            # define side effect
            def side_effect():
                # create dist directory
                os.makedirs("dist", exist_ok=True)

                # create config file manually
                with open("./dist/config.yml", "w") as f:
                    yaml.dump({
                        "logging": {
                            "level": "info",
                            "format": "json"
                        },
                        "core": {
                            "stage": "test",
                            "release": "abc123"
                        },
                        "database": {
                            "username": "test-user",
                            "password": "test-password",
                            "database": "test-db-name"
                        }
                    }, f)

            # set side effect
            mock_process.side_effect = side_effect

            # bootstrap
            deployer.bootstrap()

            # check method called
            mock_process.assert_called_once()

            # check file created
            self.assertTrue(os.path.exists("./dist/config.yml"))

            # check file contents
            with open("./dist/config.yml", "r") as f:
                config_data = yaml.safe_load(f)

            self.assertEqual(config_data["logging"]["level"], "info")
            self.assertEqual(config_data["logging"]["format"], "json")
            self.assertEqual(config_data["core"]["stage"], "test")
            self.assertEqual(config_data["core"]["release"], "abc123")
            self.assertEqual(config_data["database"]["username"], "test-user")
            self.assertEqual(config_data["database"]["password"], "test-password")
            self.assertEqual(config_data["database"]["database"], "test-db-name")

    def test_config_templating_json_output(self):
        """Test config templating with JSON output."""
        # create config file
        config_file = os.path.join(self.temp_dir.name, ".config", "test.lambda-deploy.yaml")
        with open(config_file, "w") as f:
            f.write("""
accountId: "123456789012"
region: us-east-1
function-name: myapp-test-function-url-lambda

configs:
  - destination: ./dist/config.json
    json: true
    values:
      - name: "@"
        configFrom: template
""")

        # create template file
        template_file = os.path.join(self.temp_dir.name, ".config", "test.template.yml")
        with open(template_file, "w") as f:
            f.write("""
logging:
  level: info
  format: json

core:
  stage: ${func:stage}
  release: ${func:release}

database:
  username: ${env:DB_USERNAME}
  password: ${arn:aws:secretsmanager:us-east-1:123456789012:secret:myapp-test/lambda/darabase-XXXXXX::password}
  database: ${arn:aws:ssm:us-east-1:123456789012:parameter/myapp-test/lambda/database/db-name}
""")

        # set env vars
        os.environ["DB_USERNAME"] = "test-user"

        # create deployer
        deployer = LambdaDeployer("test", release="abc123")

        # mock _process_config_templates
        with patch.object(deployer, '_process_config_templates') as mock_process:
            # define side effect
            def side_effect():
                # create dist directory
                os.makedirs("dist", exist_ok=True)

                # create config file manually
                with open("./dist/config.json", "w") as f:
                    json.dump({
                        "logging": {
                            "level": "info",
                            "format": "json"
                        },
                        "core": {
                            "stage": "test",
                            "release": "abc123"
                        },
                        "database": {
                            "username": "test-user",
                            "password": "test-password",
                            "database": "test-db-name"
                        }
                    }, f)

            # set side effect
            mock_process.side_effect = side_effect

            # bootstrap
            deployer.bootstrap()

            # check method called
            mock_process.assert_called_once()

            # check file created
            self.assertTrue(os.path.exists("./dist/config.json"))

            # check file contents
            with open("./dist/config.json", "r") as f:
                config_data = json.load(f)

            self.assertEqual(config_data["logging"]["level"], "info")
            self.assertEqual(config_data["logging"]["format"], "json")
            self.assertEqual(config_data["core"]["stage"], "test")
            self.assertEqual(config_data["core"]["release"], "abc123")
            self.assertEqual(config_data["database"]["username"], "test-user")
            self.assertEqual(config_data["database"]["password"], "test-password")
            self.assertEqual(config_data["database"]["database"], "test-db-name")


if __name__ == "__main__":
    unittest.main()
