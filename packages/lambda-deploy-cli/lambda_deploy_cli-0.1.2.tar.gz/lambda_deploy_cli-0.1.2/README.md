# Lambda Deploy

A tool for deploying AWS Lambda functions with proper environment variable management and configuration templating.

## Features

- Bootstrap environment variables from various sources (AWS Parameter Store, Secrets Manager, environment variables)
- Deploy Lambda functions with proper environment variables
- Support for multiple stages (dev, stg, prd)
- Configuration templating with variable substitution
- Validate AWS credentials against account ID

## Installation

### From PyPI

```bash
pip install lambda-deploy-cli
```

### From Source

```bash
# Clone the repository
git clone https://github.com/povio/lambda-deploy.git
cd lambda-deploy

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install in development mode
pip install -e .
```

## Usage

### Configuration

Create a configuration file for each stage in the `.config` directory:


```yaml
# .config/dev.lambda-deploy.yml
accountId: "123456789012"
region: us-east-1
function-name: my-lambda-function
build-dir: "dist"

configs:
  destination: ./dist/config.yml
  values:
    - name: "@"
      configFrom: template
```

### Configuration Templating

You can use configuration templating to generate configuration files from templates:


```yaml
# .config/dev.template.yml
app:
  stage: ${func:stage}
  release: ${func:release}
  logLevel: ${LOG_LEVEL}

api:
  key: arn:aws:ssm:us-east-1:123456789012:parameter/my-service/dev/api-key
  url: https://api.dev.example.com

database:
  connection: arn:aws:secretsmanager:us-east-1:123456789012:secret:my-service/dev/db-123456::connectionString
  maxConnections: 5
```

### Template Examples

#### Simple Template

For lambda Environment Vars use this format and set `json: true` in main stage config.
```yaml
# .config/dev.template.yml
API_KEY: arn:aws:ssm:us-east-1:123456789012:parameter/dev/lambda/api-key
API_SECRET: arn:aws:secretsmanager:us-east-1:123456789012:secret:dev/lambda/somevar-123456::somevar
```

#### Nested Template with Function Variables

```yaml
# .config/dev.template.yml
app:
  stage: ${func:stage}
  release: ${func:release}
  logLevel: ${LOG_LEVEL}

api:
  key: arn:aws:ssm:us-east-1:123456789012:parameter/my-service/dev/api-key
  url: https://api.dev.example.com

database:
  connection: arn:aws:secretsmanager:us-east-1:123456789012:secret:my-service/dev/db-123456::connectionString
  maxConnections: 5
```

#### Multiple Configuration Outputs

```yaml
# .config/dev.lambda-deploy.yml
accountId: "123456789012"
region: us-east-1
function-name: my-lambda-function
build-dir: "dist"

configs:
  # Generate YAML config file
  - destination: ./dist/config.yml
    values:
      - name: "@"
        configFrom: template

  # Generate JSON environment variables file
  - destination: dev-vars.json
    json: true
    values:
      - name: "dev"
        configFrom: template
```

The template supports the following variable substitutions:
- `${func:stage}`: The current stage (dev, stg, prd)
- `${func:release}`: The release identifier (git commit hash)
- `${ENV_VAR}`: Environment variables
- AWS Parameter Store references: Values starting with `arn:aws:ssm:` will be resolved from AWS Parameter Store
- AWS Secrets Manager references: Values starting with `arn:aws:secretsmanager:` will be resolved from AWS Secrets Manager

### Command-Line Interface

The tool provides a command-line interface with the following commands:

```bash
# Show help
lambda-deploy --help

# Show command-specific help
lambda-deploy bootstrap --help
lambda-deploy deploy --help
lambda-deploy info --help
```

### Bootstrap Environment Variables

```bash
lambda-deploy bootstrap --stage dev
```

This will resolve all variables from the configuration and save them to a file.

### Deploy Lambda Function

```bash
lambda-deploy deploy --stage dev --release abc123
```

This will update the Lambda function with the resolved environment variables and deploy the code from the `dist` directory.

If no `{stage}-vars.json` file exists, the environment variables update will be skipped automatically, and only the function code will be updated.

### View Lambda Function Information

```bash
lambda-deploy info --stage dev
```

This will display information about the Lambda function configuration, including environment variables and function details.

### Global Options

- `--verbose`, `-v`: Enable verbose output
- `--help`: Show help message and exit
- `--version`: Show version and exit

### Command Options

#### Common Options

- `--stage`: Deployment stage (dev, stg, prd). Can also be set via the `STAGE` environment variable.
- `--config-dir`: Directory containing configuration files. Defaults to `.config`.
- `--release`: Release identifier (git commit hash). Can also be set via the `RELEASE` environment variable.

#### Bootstrap and Deploy Commands

- `--source`: Path to a directory containing the source code to deploy. Overrides the `build-dir` from the configuration.
- `--env-vars`: Path to a JSON file containing environment variables. Overrides the default `<stage>-vars.json` file.

#### Deploy Command Only

- `--skip-env-update`: Skip updating environment variables.

## Complete Workflow Example

### 1. Project Structure

```
my-lambda-project/
├── .config/
│   ├── dev.lambda-deploy.yml
│   ├── stg.lambda-deploy.yml
│   ├── prd.lambda-deploy.yml
│   ├── dev.template.yml
│   ├── stg.template.yml
│   └── prd.template.yml
├── src/
│   ├── index.tjs
│   └── ...
├── dist/
│   ├── index.js (bundled)
│   └── ...
└── package.json
```

## Development

### Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Testing

```bash
pytest
pytest --cov=lambda_deploy
python -m unittest discover tests
```

### Releasing New Versions

This project uses GitHub Actions to automatically publish new releases to PyPI.

1. Update the version in `lambda_deploy/__init__.py`:
   - For regular releases: `"0.1.0"`, `"0.2.0"`, etc.
   - For beta releases: `"0.1.0b1"`, `"0.1.0b2"`, etc.
   - For release candidates: `"0.1.0rc1"`, `"0.1.0rc2"`, etc.

2. Create and push a new tag matching the version:
   ```bash
   git tag v0.1.1b1
   git push origin v0.1.1b1
   ```

3. The GitHub Actions workflow will automatically:
   - Run the test workflow on multiple Python versions (3.8, 3.9, 3.10, 3.12)
   - Build the package (only if all tests pass)
   - Publish it to PyPI (only if all tests pass)

Alternatively, you can create a new release through the GitHub UI:
   - Go to the repository's "Releases" section
   - Click "Draft a new release"
   - Create a new tag matching the version (e.g., `v0.1.0`, `v0.1.0b1`)
   - Add release notes
   - Publish the release

### Beta Versions

Beta versions (e.g., `0.1.0b1`) will be published to PyPI.

To install a beta version from PyPI:

```bash
pip install lambda-deploy-cli==0.1.0b1
```

To install the latest beta version:

```bash
pip install --pre lambda-deploy-cli
```
