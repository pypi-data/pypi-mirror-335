#!/usr/bin/env python3
"""
aws-co: A wrapper for AWS CLI that assumes a role before running commands.
"""

import os
import sys
import json
import click
import subprocess
import logging
import signal
from pathlib import Path

# Set up logging
logger = logging.getLogger('awsco')
handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Handle broken pipe errors gracefully
def handle_broken_pipe(*args):
    # Python flushes standard streams on exit; redirect remaining output
    # to /dev/null to avoid another BrokenPipeError at shutdown
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, sys.stdout.fileno())
    sys.exit(0)  # Exit with success code

# Register the signal handler
signal.signal(signal.SIGPIPE, handle_broken_pipe)

# Default values
DEFAULT_PROFILE = "saas-co"
DEFAULT_ROLE = "ESW-CO-PowerUser-P2"
CONFIG_FILE = Path.home() / ".aws-co.json"

def load_config():
    """Load configuration from config file."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning(f"Error parsing config file {CONFIG_FILE}. Using default configuration.")
            return {
                "default_profile": DEFAULT_PROFILE,
                "default_role": DEFAULT_ROLE,
                "recent_accounts": []
            }
    return {
        "default_profile": DEFAULT_PROFILE,
        "default_role": DEFAULT_ROLE,
        "recent_accounts": []
    }

def save_config(config):
    """Save configuration to config file."""
    # Create a backup of the config file if it exists
    if CONFIG_FILE.exists():
        backup_file = CONFIG_FILE.with_suffix('.json.bak')
        import shutil
        shutil.copy2(CONFIG_FILE, backup_file)
        logger.debug(f"Created backup of config file at {backup_file}")
        
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    logger.debug(f"Saved configuration to {CONFIG_FILE}")

def assume_role(account_id, profile, role_name, session_name):
    """Assume the specified role and return credentials."""
    cmd = [
        "aws", "sts", "assume-role",
        "--role-arn", f"arn:aws:iam::{account_id}:role/{role_name}",
        "--role-session-name", session_name,
        "--profile", profile
    ]
    
    logger.debug(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        credentials = json.loads(result.stdout)["Credentials"]
        logger.debug("Successfully assumed role")
        return {
            "AWS_ACCESS_KEY_ID": credentials["AccessKeyId"],
            "AWS_SECRET_ACCESS_KEY": credentials["SecretAccessKey"],
            "AWS_SESSION_TOKEN": credentials["SessionToken"]
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"Error assuming role: {e.stderr}")
        sys.exit(1)
    except json.JSONDecodeError:
        logger.error("Failed to parse AWS credentials response")
        sys.exit(1)
    except KeyError:
        logger.error("Credentials not found in AWS response")
        sys.exit(1)

def update_recent_accounts(config, account_id):
    """Update the list of recently used accounts."""
    if account_id in config["recent_accounts"]:
        config["recent_accounts"].remove(account_id)
    config["recent_accounts"].insert(0, account_id)
    config["recent_accounts"] = config["recent_accounts"][:5]  # Keep only 5 most recent
    save_config(config)
    logger.debug(f"Updated recent accounts list: {config['recent_accounts']}")

def run_aws_command(account_id, profile, role_name, aws_args):
    """Run an AWS command with assumed role credentials."""
    session_name = f"aws-co-session-{os.getpid()}"
    
    click.echo(f"Assuming role {role_name} in account {account_id} using profile {profile}...")
    
    # Assume the role
    credentials = assume_role(account_id, profile, role_name, session_name)
    
    # Update recent accounts
    config = load_config()
    update_recent_accounts(config, account_id)
    
    # Run the AWS command with the assumed role credentials
    env = os.environ.copy()
    env.update(credentials)
    
    if not aws_args:
        click.echo("No AWS command specified. Credentials are:")
        click.echo(f"AWS_ACCESS_KEY_ID={credentials['AWS_ACCESS_KEY_ID']}")
        click.echo(f"AWS_SECRET_ACCESS_KEY={credentials['AWS_SECRET_ACCESS_KEY'][:5]}...")
        click.echo(f"AWS_SESSION_TOKEN={credentials['AWS_SESSION_TOKEN'][:10]}...")
        return
    
    cmd = ["aws"] + list(aws_args)
    click.echo(f"Running: {' '.join(cmd)}")
    logger.debug(f"Full command: {cmd}")
    
    # Use os.execvpe to replace the current process with the AWS command
    # This avoids broken pipe errors when piping output
    try:
        os.execvpe("aws", cmd, env)
    except Exception as e:
        logger.error(f"Error running AWS command: {e}")
        sys.exit(1)

@click.command(name="config")
@click.option('--account', '-a', help='Target AWS account ID')
@click.option('--profile', '-p', help=f'AWS profile to use (default: {DEFAULT_PROFILE})')
@click.option('--role', '-r', help=f'Role name to assume (default: {DEFAULT_ROLE})')
@click.option('--set-profile', help='Set default AWS profile')
@click.option('--set-role', help='Set default role name')
@click.option('--debug', is_flag=True, help='Enable debug logging')
def config_command(account, profile, role, set_profile, set_role, debug):
    """Configure default settings."""
    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    config = load_config()
    
    # Set defaults from config if not provided
    profile = profile or config.get("default_profile", DEFAULT_PROFILE)
    role = role or config.get("default_role", DEFAULT_ROLE)
    
    # Only assume role if account is provided
    if account:
        # Assume role to validate credentials
        session_name = f"aws-co-session-{os.getpid()}"
        click.echo(f"Assuming role {role} in account {account} using profile {profile}...")
        assume_role(account, profile, role, session_name)
        
        # Update recent accounts
        update_recent_accounts(config, account)
    
    if set_profile:
        config["default_profile"] = set_profile
        click.echo(f"Default profile set to: {set_profile}")
    
    if set_role:
        config["default_role"] = set_role
        click.echo(f"Default role set to: {set_role}")
    
    if set_profile or set_role:
        save_config(config)
    
    # Display current config
    click.echo("Current configuration:")
    click.echo(f"Default profile: {config.get('default_profile', DEFAULT_PROFILE)}")
    click.echo(f"Default role: {config.get('default_role', DEFAULT_ROLE)}")
    if config.get("recent_accounts"):
        click.echo("Recent accounts:")
        for acct in config.get("recent_accounts", []):
            click.echo(f"  - {acct}")

@click.command(name="recent")
@click.option('--account', '-a', help='Target AWS account ID')
@click.option('--profile', '-p', help=f'AWS profile to use (default: {DEFAULT_PROFILE})')
@click.option('--role', '-r', help=f'Role name to assume (default: {DEFAULT_ROLE})')
@click.option('--debug', is_flag=True, help='Enable debug logging')
def recent_command(account, profile, role, debug):
    """Show recently used accounts."""
    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    config = load_config()
    
    # Set defaults from config if not provided
    profile = profile or config.get("default_profile", DEFAULT_PROFILE)
    role = role or config.get("default_role", DEFAULT_ROLE)
    
    # Only assume role if account is provided
    if account:
        # Assume role to validate credentials
        session_name = f"aws-co-session-{os.getpid()}"
        click.echo(f"Assuming role {role} in account {account} using profile {profile}...")
        assume_role(account, profile, role, session_name)
        
        # Update recent accounts
        update_recent_accounts(config, account)
    
    accounts = config.get("recent_accounts", [])
    
    if not accounts:
        click.echo("No recent accounts found.")
        return
    
    click.echo("Recent accounts:")
    for acct in accounts:
        click.echo(f"  - {acct}")

@click.command(name="setup")
@click.option('--saas-account', '-s', required=True, help='SaaS AWS account ID')
@click.option('--target-account', '-t', help='Target AWS account ID (optional)')
@click.option('--profile', '-p', help=f'AWS profile to use (default: {DEFAULT_PROFILE})')
@click.option('--role', '-r', help=f'Role name to assume (default: {DEFAULT_ROLE})')
@click.option('--debug', is_flag=True, help='Enable debug logging')
def setup_command(saas_account, target_account, profile, role, debug):
    """
    Quick setup for SaaS and target accounts.
    
    This command sets up the default SaaS account profile and tests access to the target account.
    The target account is optional - if not provided, you'll need to specify it with each command.
    
    Examples:
        aws-co setup -s 123456789012 -t 987654321098  # Set up with both accounts
        aws-co setup -s 123456789012                  # Set up with just SaaS account
    """
    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    config = load_config()
    
    # Set defaults from config if not provided
    profile = profile or config.get("default_profile", DEFAULT_PROFILE)
    role = role or config.get("default_role", DEFAULT_ROLE)
    
    click.echo(f"Setting up aws-co with SaaS account {saas_account}")
    if target_account:
        click.echo(f"and target account {target_account}")
    
    # Check if AWS CLI is installed
    try:
        subprocess.run(["aws", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        click.echo("AWS CLI not found. Please install it first: https://aws.amazon.com/cli/")
        sys.exit(1)
    
    # Check if AWS profile exists
    try:
        subprocess.run(
            ["aws", "sts", "get-caller-identity", "--profile", profile], 
            capture_output=True, 
            check=True
        )
        click.echo(f"✅ AWS profile '{profile}' is configured correctly")
    except subprocess.CalledProcessError:
        click.echo(f"❌ AWS profile '{profile}' not found or not configured correctly")
        click.echo(f"Please run: aws configure --profile {profile}")
        sys.exit(1)
    
    # Test assuming role in target account if provided
    if target_account:
        try:
            session_name = f"aws-co-setup-{os.getpid()}"
            click.echo(f"Testing role assumption: {role} in account {target_account} using profile {profile}...")
            assume_role(target_account, profile, role, session_name)
            click.echo(f"✅ Successfully assumed role {role} in account {target_account}")
            
            # Update recent accounts
            if target_account in config.get("recent_accounts", []):
                config["recent_accounts"].remove(target_account)
            config["recent_accounts"].insert(0, target_account)
            config["recent_accounts"] = config["recent_accounts"][:5]  # Keep only 5 most recent
            
            # Set default target account if requested
            config["default_target"] = target_account
            click.echo(f"✅ Set {target_account} as default target account")
        except Exception as e:
            click.echo(f"❌ Failed to assume role: {e}")
            sys.exit(1)
    
    # Update config
    config["default_profile"] = profile
    config["default_role"] = role
    config["saas_account"] = saas_account
    
    save_config(config)
    
    click.echo("\n✅ Setup complete! Your configuration has been saved.")
    
    if target_account:
        click.echo("\nYou can now run commands without specifying the target account:")
        click.echo(f"  aws-co run s3 ls")
        click.echo(f"  aws-co run ec2 describe-instances")
    else:
        click.echo("\nYou can now run commands by specifying the target account:")
        click.echo(f"  aws-co run -a TARGET_ACCOUNT_ID s3 ls")
        click.echo(f"  aws-co run -a TARGET_ACCOUNT_ID ec2 describe-instances")

@click.command(name="run")
@click.option('--account', '-a', help='Target AWS account ID')
@click.option('--profile', '-p', help=f'AWS profile to use (default: {DEFAULT_PROFILE})')
@click.option('--role', '-r', help=f'Role name to assume (default: {DEFAULT_ROLE})')
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.argument('aws_args', nargs=-1, type=click.UNPROCESSED)
def run_command(account, profile, role, debug, aws_args):
    """
    Run AWS CLI commands with assumed role credentials.
    
    This tool first assumes a role in the specified account, then runs
    the AWS CLI command with those credentials.
    
    Examples:
        aws-co run -a 123456789012 s3 ls
        aws-co run -a 123456789012 -p my-profile ec2 describe-instances
        aws-co run s3 ls  # Uses default target account if set during setup
    """
    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Load config
    config = load_config()
    logger.debug(f"Loaded configuration: {config}")
    
    # Set defaults from config if not provided
    profile = profile or config.get("default_profile", DEFAULT_PROFILE)
    role = role or config.get("default_role", DEFAULT_ROLE)
    
    # Use default target account if not specified
    if not account and "default_target" in config:
        account = config["default_target"]
        logger.debug(f"Using default target account: {account}")
    
    if not account:
        logger.error("No target account specified and no default target account set.")
        click.echo("Error: Target account ID is required. Please specify with -a/--account.")
        click.echo("       Or set a default target account with: aws-co setup -s SAAS_ID -t TARGET_ID")
        sys.exit(1)
    
    logger.debug(f"Using account: {account}, profile: {profile}, role: {role}")
    
    run_aws_command(account, profile, role, aws_args)

@click.group()
def cli():
    """
    aws-co: Run AWS CLI commands with assumed role credentials.
    """
    pass

# Add commands to the CLI group
cli.add_command(run_command)
cli.add_command(config_command)
cli.add_command(recent_command)
cli.add_command(setup_command)

def main():
    """Entry point for the CLI."""
    try:
        cli()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
