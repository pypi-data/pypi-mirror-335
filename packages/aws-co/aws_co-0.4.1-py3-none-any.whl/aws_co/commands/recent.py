#!/usr/bin/env python3
"""
Recent command for aws-co.
"""

import os
import logging
import click

from ..config import load_config, update_recent_accounts
from ..config import DEFAULT_ROLE, DEFAULT_SOURCE_PROFILE, DEFAULT_SAAS_ROLE
from ..credentials import assume_role

# Set up logging
logger = logging.getLogger('awsco.commands.recent')

@click.command(name="recent")
@click.option('--account', '-a', help='Target AWS account ID')
@click.option('--role', '-r', help=f'Role name to assume (default: {DEFAULT_ROLE})')
@click.option('--source-profile', '-s', help=f'Source profile for role chaining (default: {DEFAULT_SOURCE_PROFILE})')
@click.option('--saas-account', help='SaaS account ID for role chaining')
@click.option('--debug', is_flag=True, help='Enable debug logging')
def recent_command(account, role, source_profile, saas_account, debug):
    """Show recently used accounts."""
    if debug:
        logging.getLogger('awsco').setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    config = load_config()
    
    # Set defaults from config if not provided
    role = role or config.get("default_role", DEFAULT_ROLE)
    saas_role = config.get("default_saas_role", DEFAULT_SAAS_ROLE)
    saas_account = saas_account or config.get("saas_account")
    source_profile = source_profile or config.get("default_source_profile", DEFAULT_SOURCE_PROFILE)
    
    # Test role assumption if account is provided
    if account:
        session_name = f"aws-co-recent-{os.getpid() % 10000}"
        
        if saas_account and saas_role:
            click.echo(f"Testing role chaining...")
            click.echo(f"First assuming role {saas_role} in SaaS account {saas_account} using profile {source_profile}...")
            click.echo(f"Then assuming role {role} in target account {account}...")
            assume_role(account, "default", role, session_name, source_profile, saas_account, saas_role)
        else:
            click.echo(f"Assuming role {role} in account {account} using profile {DEFAULT_SOURCE_PROFILE}...")
            assume_role(account, DEFAULT_SOURCE_PROFILE, role, session_name)
        
        # Update recent accounts
        update_recent_accounts(config, account)
    
    # Show recent accounts
    click.echo("\nRecent accounts:")
    if "recent_accounts" in config and config["recent_accounts"]:
        for i, acc in enumerate(config["recent_accounts"], 1):
            if "default_target" in config and acc == config["default_target"]:
                click.echo(f"{i}. {acc} (default)")
            else:
                click.echo(f"{i}. {acc}")
    else:
        click.echo("No recent accounts found. Use aws-co run to add some!")
    
    # Show how to use recent accounts
    click.echo("\nTo use a recent account:")
    click.echo("aws-co run -a ACCOUNT_ID [AWS COMMAND]")
    
    if "default_target" in config:
        click.echo("\nOr use the default target account:")
        click.echo("aws-co run [AWS COMMAND]")
