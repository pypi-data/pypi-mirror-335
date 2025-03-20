# AWS-CO: AWS Role Assumption CLI Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful CLI tool that simplifies working with multiple AWS accounts by automating role assumption and credential management. Perfect for DevOps engineers, cloud administrators, and anyone who regularly works across multiple AWS accounts.

## Features

- **Seamless Role Assumption**: Automatically assume IAM roles across accounts
- **Command Passthrough**: Run any AWS CLI command with assumed credentials
- **Profile Management**: Configure and use different AWS profiles
- **Account History**: Track and quickly access recently used accounts
- **Customizable Defaults**: Set your preferred profile and role name
- **User-Friendly Interface**: Comprehensive help and error messages
- **Configuration Persistence**: Settings stored in `~/.aws-co.json`
- **Quick Setup**: Easy configuration with the setup command
- **Role Chaining**: Assume a role in a SaaS account, then another role in a target account

## Installation

### Prerequisites

- Python 3.6+
- AWS CLI installed and configured
- AWS credentials with permission to assume roles

### Install from PyPI

```bash
# Install globally (system-wide)
pip install aws-co

# Or if you prefer using a virtual environment (optional)
python -m venv aws_co_env
source aws_co_env/bin/activate  # On Windows: aws_co_env\Scripts\activate
pip install aws-co
```

### Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/aws-co.git
cd aws-co

# Install the package
pip install --user -e .
```

### Verify Installation

```bash
aws-co --help
```

## Quick Start

The fastest way to get started is to use the setup command:

```bash
# Set up with both SaaS account and a target account (recommended)
aws-co setup -s YOUR_SAAS_ACCOUNT_ID -t YOUR_TARGET_ACCOUNT_ID

# Or set up with just the SaaS account
aws-co setup -s YOUR_SAAS_ACCOUNT_ID

# Set up with role chaining (source profile → SaaS account → target account)
aws-co setup -s YOUR_SAAS_ACCOUNT_ID -t YOUR_TARGET_ACCOUNT_ID --source-profile your-profile
```

This will:
1. Verify your AWS CLI installation
2. Check your AWS profile configuration
3. Test role assumption in the target account (if provided)
4. Save your configuration for future use

When you set up with both accounts, you can run commands without specifying the target account each time:

```bash
# With default target account set
aws-co run s3 ls

# With explicit target account
aws-co run -a 123456789012 s3 ls
```

## Usage

### Basic Usage

```bash
# Format
aws-co [COMMAND] [OPTIONS]

# Example: List S3 buckets in account 123456789012
aws-co run -a 123456789012 s3 ls
```

### Available Commands

```
Commands:
  run     Run AWS CLI commands with assumed role credentials
  config  Configure default settings
  recent  Show recently used accounts
  setup   Quick setup for SaaS and target accounts
```

### Command Options

```
Options for run command:
  -a, --account TEXT       Target AWS account ID (optional if default target is set)
  -r, --role TEXT          Role name to assume (default: ESW-CO-PowerUser-P2)
  -s, --source-profile TEXT Source profile for role chaining (defaults to "default" if not specified)
  --saas-account TEXT      SaaS account ID for role chaining
  --saas-role TEXT         SaaS role name for role chaining
  --debug                  Enable debug logging
  --help                   Show this message and exit.
```

### Configuration

Set default role and SaaS role:

```bash
aws-co config --set-role MyRoleName --set-saas-role MySaaSRoleName --set-source-profile my-profile
```

View current configuration:

```bash
aws-co config
```

### Recent Accounts

View recently used accounts:

```bash
aws-co recent
```

## Examples

### Basic AWS Commands

```bash
# Get caller identity
aws-co run -a 123456789012 sts get-caller-identity

# List EC2 instances
aws-co run -a 123456789012 ec2 describe-instances

# List CloudFormation stacks
aws-co run -a 123456789012 cloudformation list-stacks

# Using role chaining (source profile → SaaS account → target account)
aws-co run -a 123456789012 -s my-profile s3 ls
```

### Cost Optimization

```bash
# Get EC2 reservation recommendations
aws-co run -a 123456789012 ce get-reservation-purchase-recommendation \
  --service "Amazon Elastic Compute Cloud - Compute" \
  --term "ONE_YEAR" \
  --payment-option "NO_UPFRONT"

# Get RDS reservation recommendations
aws-co run -a 123456789012 ce get-reservation-purchase-recommendation \
  --service "Amazon Relational Database Service" \
  --term "ONE_YEAR" \
  --payment-option "NO_UPFRONT"
```

### Using Different Profiles and Roles

```bash
# Use a specific profile
aws-co run -a 123456789012 -p production-profile s3 ls

# Assume a specific role
aws-co run -a 123456789012 -r AdminRole ec2 describe-instances
```

## Configuration File

The configuration file is stored at `~/.aws-co.json` and has the following structure:

```json
{
  "default_role": "ESW-CO-PowerUser-P2",
  "default_saas_role": "ESW-CO-PowerUser-P2",
  "default_source_profile": "default",
  "saas_account": "123456789012",
  "default_target": "987654321098",
  "recent_accounts": [
    "987654321098",
    "210987654321"
  ]
}
```

## Role Chaining

Starting with version 0.4.0, aws-co supports role chaining. This allows you to:

1. Assume a role in the SaaS account using your own AWS credentials
2. Then use those credentials to assume a role in the target account

This is useful when you don't have direct access to the SaaS account, but you have a role in your own AWS account that can assume a role in the SaaS account.

### Setting up Role Chaining

You can set up role chaining during the initial setup:

```bash
aws-co setup -s 123456789012 -t 987654321098 --source-profile my-profile
```

Where:
- `123456789012` is your SaaS account ID
- `987654321098` is your target account ID
- `my-profile` is your AWS profile with credentials (defaults to "default" if not specified)

### Using Role Chaining

Once set up, you can use role chaining with any command:

```bash
# Using default source profile
aws-co run s3 ls

# Specifying a different source profile
aws-co run -s another-profile s3 ls
```

### Role Chaining Configuration

You can configure role chaining settings with the config command:

```bash
# Set default source profile
aws-co config --set-source-profile my-profile

# Set default SaaS role
aws-co config --set-saas-role MyCustomRole
```

By default, aws-co will use:
- The "default" AWS profile as the source profile if not specified
- The "ESW-CO-PowerUser-P2" role in the SaaS account if not specified

## Troubleshooting

### Common Issues

1. **Role assumption fails**: Ensure your AWS credentials have permission to assume the target role
2. **Command not found**: Make sure `~/.local/bin` is in your PATH
3. **Invalid credentials**: Check that your AWS profile is correctly configured

### Debug Mode

Add `--debug` to see detailed debugging information:

```bash
aws-co run -a 123456789012 --debug s3 ls
```

## For Friends and Team Members

If you received this tool from a friend or team member:

1. Install the package:
   ```bash
   pip install aws-co
   ```

2. Run the setup command with your SaaS account ID and optionally a target account ID:
   ```bash
   # Set up with both accounts (recommended for convenience)
   aws-co setup -s YOUR_SAAS_ACCOUNT_ID -t YOUR_TARGET_ACCOUNT_ID
   
   # Or set up with just the SaaS account
   aws-co setup -s YOUR_SAAS_ACCOUNT_ID
   ```

3. Start using the tool:
   ```bash
   # If you set a default target account:
   aws-co run s3 ls
   
   # Otherwise, specify the target account each time:
   aws-co run -a YOUR_TARGET_ACCOUNT_ID s3 ls
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
