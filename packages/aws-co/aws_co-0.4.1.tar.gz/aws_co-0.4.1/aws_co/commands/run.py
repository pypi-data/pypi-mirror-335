#!/usr/bin/env python3
"""
Run command for aws-co.
"""

import logging
import click

from ..config import load_config, DEFAULT_ROLE, DEFAULT_SOURCE_PROFILE, DEFAULT_SAAS_ROLE
from ..credentials import run_aws_command
from ..config import update_recent_accounts

# Set up logging
logger = logging.getLogger('awsco.commands.run')

@click.command(name="run")
@click.option('--account', '-a', help='Target AWS account ID (optional if default target is set)')
@click.option('--role', '-r', help=f'Role name to assume (default: {DEFAULT_ROLE})')
@click.option('--source-profile', '-s', help=f'Source profile for role chaining (default: {DEFAULT_SOURCE_PROFILE})')
@click.option('--saas-account', help='SaaS account ID for role chaining')
@click.option('--saas-role', help=f'SaaS role name for role chaining (default: {DEFAULT_SAAS_ROLE})')
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.argument('aws_args', nargs=-1)
def run_command(account, role, source_profile, saas_account, saas_role, debug, aws_args):
    """
    Run AWS CLI commands with assumed role credentials.
    
    This tool first assumes a role in the specified account, then runs
    the AWS CLI command with those credentials.
    
    You can use role chaining by providing a SaaS account:
    - source_profile: Your local AWS profile with credentials (default: {DEFAULT_SOURCE_PROFILE})
    - saas_account: The SaaS account ID (uses config if not specified)
    - saas_role: The role to assume in the SaaS account (default: {DEFAULT_SAAS_ROLE})
    
    Examples:
        aws-co run -a XXXXXXXXXXXXXX s3 ls
        aws-co run -a XXXXXXXXXXXXXX -r CustomRoleName ec2 describe-instances
        aws-co run s3 ls  # Uses default target account if set during setup
        aws-co run -s my-profile --saas-account XXXXXXXXXXXXXX s3 ls  # Uses role chaining
    """
    if debug:
        logging.getLogger('awsco').setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    config = load_config()
    
    # Set defaults from config if not provided
    role = role or config.get("default_role", DEFAULT_ROLE)
    saas_role = saas_role or config.get("default_saas_role", DEFAULT_SAAS_ROLE)
    source_profile = source_profile or config.get("default_source_profile", DEFAULT_SOURCE_PROFILE)
    saas_account = saas_account or config.get("saas_account")
    
    # If account not provided, use default target
    if not account:
        account = config.get("default_target")
        if not account:
            click.echo("No account specified and no default target set.")
            click.echo("Please specify an account with -a/--account or set a default target with setup.")
            click.echo("Example: aws-co run -a 123456789012 s3 ls")
            return
    
    logger.debug(f"Using account: {account}, role: {role}")
    
    if saas_account and saas_role:
        logger.debug(f"Using role chaining with source profile: {source_profile}")
        run_aws_command(account, "default", role, aws_args, source_profile, saas_account, saas_role)
    else:
        run_aws_command(account, source_profile, role, aws_args)
    
    # Update recent accounts (this won't actually happen due to os.execvpe in run_aws_command)
    update_recent_accounts(config, account)
