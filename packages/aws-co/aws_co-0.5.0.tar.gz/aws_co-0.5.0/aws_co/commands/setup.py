#!/usr/bin/env python3
"""
Setup command for aws-co.
"""

import os
import sys
import logging
import subprocess
import click

from ..config import load_config, save_config, update_recent_accounts
from ..config import DEFAULT_ROLE, DEFAULT_SOURCE_PROFILE, DEFAULT_SAAS_ROLE, DEFAULT_PROFILE
from ..credentials import assume_role
from ..utils import check_aws_cli_installed, check_aws_profile

# Set up logging
logger = logging.getLogger('awsco.commands.setup')

@click.command(name="setup")
@click.option('--saas-account', '-s', required=True, help='SaaS AWS account ID')
@click.option('--target-account', '-t', help='Target AWS account ID (optional)')
@click.option('--role', '-r', help=f'Role name to assume (default: {DEFAULT_ROLE})')
@click.option('--saas-role', help=f'SaaS role name for role chaining (default: {DEFAULT_SAAS_ROLE})')
@click.option('--source-profile', help=f'Source profile for role chaining (default: {DEFAULT_SOURCE_PROFILE})')
@click.option('--debug', is_flag=True, help='Enable debug logging')
def setup_command(saas_account, target_account, role, saas_role, source_profile, debug):
    """
    Quick setup for SaaS and target accounts.
    
    This command sets up the default SaaS account profile and tests access to the target account.
    The target account is optional - if not provided, you'll need to specify it with each command.
    
    You can use role chaining by providing a source profile and SaaS role:
    - source_profile: Your local AWS profile with credentials (default: {DEFAULT_SOURCE_PROFILE})
    - saas_account: The SaaS account ID
    - saas_role: The role to assume in the SaaS account (default: {DEFAULT_SAAS_ROLE})
    - target_account: The final target account ID
    
    Examples:
        aws-co setup -s 123456789012 -t 987654321098  # Set up with both accounts
        aws-co setup -s 123456789012                  # Set up with just SaaS account
        aws-co setup -s 123456789012 -t 987654321098 --source-profile my-profile  # Use role chaining
    """
    if debug:
        logging.getLogger('awsco').setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    config = load_config()
    
    # Set defaults from config if not provided
    role = role or config.get("default_role", DEFAULT_ROLE)
    saas_role = saas_role or config.get("default_saas_role", DEFAULT_SAAS_ROLE)
    source_profile = source_profile or config.get("default_source_profile", DEFAULT_SOURCE_PROFILE)
    
    click.echo(f"Setting up aws-co with SaaS account {saas_account}")
    if target_account:
        click.echo(f"and target account {target_account}")
    
    # Check if AWS CLI is installed
    if not check_aws_cli_installed():
        click.echo("AWS CLI not found. Please install it first: https://aws.amazon.com/cli/")
        sys.exit(1)
    
    # Check if AWS profile exists
    if not check_aws_profile(source_profile):
        click.echo(f"❌ Source AWS profile '{source_profile}' not found or not configured correctly")
        click.echo(f"Please run: aws configure --profile {source_profile}")
        sys.exit(1)
    else:
        click.echo(f"✅ Source AWS profile '{source_profile}' is configured correctly")
    
    # Test assuming role in target account if provided
    if target_account:
        try:
            session_name = f"aws-co-setup-{os.getpid() % 10000}"
            
            click.echo(f"Testing role chaining...")
            click.echo(f"First assuming role {saas_role} in SaaS account {saas_account} using profile {source_profile}...")
            click.echo(f"Then assuming role {role} in target account {target_account}...")
            assume_role(target_account, DEFAULT_PROFILE, role, session_name, source_profile, saas_account, saas_role)
            click.echo(f"✅ Successfully chained roles through SaaS account to target account {target_account}")
            
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
    config["default_role"] = role
    config["saas_account"] = saas_account
    config["default_saas_role"] = saas_role
    config["default_source_profile"] = source_profile
    click.echo(f"✅ Set {source_profile} as default source profile for role chaining")
    
    save_config(config)
    
    click.echo("\n✅ Setup complete! Your configuration has been saved.")
    
    if target_account:
        click.echo("\nYou can now run commands with role chaining:")
        click.echo(f"  aws-co run s3 ls")
        click.echo(f"  aws-co run ec2 describe-instances")
    else:
        click.echo("\nYou can now run commands by specifying the target account:")
        click.echo(f"  aws-co run -a TARGET_ACCOUNT_ID s3 ls")
        click.echo(f"  aws-co run -a TARGET_ACCOUNT_ID ec2 describe-instances")
