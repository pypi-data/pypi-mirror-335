#!/usr/bin/env python3
"""
Config command for aws-co.
"""

import os
import logging
import click

from ..config import load_config, save_config, update_recent_accounts
from ..config import DEFAULT_ROLE, DEFAULT_SOURCE_PROFILE, DEFAULT_SAAS_ROLE
from ..credentials import assume_role

# Set up logging
logger = logging.getLogger('awsco.commands.config')

@click.command(name="config")
@click.option('--account', '-a', help='Target AWS account ID')
@click.option('--role', '-r', help=f'Role name to assume (default: {DEFAULT_ROLE})')
@click.option('--set-role', is_flag=True, help='Set default role')
@click.option('--set-saas-role', is_flag=True, help='Set default SaaS role for role chaining')
@click.option('--set-source-profile', is_flag=True, help='Set default source profile for role chaining')
@click.option('--source-profile', help=f'Source profile for role chaining (default: {DEFAULT_SOURCE_PROFILE})')
@click.option('--saas-account', help='SaaS account ID for role chaining')
@click.option('--debug', is_flag=True, help='Enable debug logging')
def config_command(account, role, set_role, set_saas_role, set_source_profile, source_profile, saas_account, debug):
    """Configure default settings."""
    if debug:
        logging.getLogger('awsco').setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    config = load_config()
    
    # Set defaults from config if not provided
    role = role or config.get("default_role", DEFAULT_ROLE)
    saas_role = config.get("default_saas_role", DEFAULT_SAAS_ROLE)
    
    # Test role assumption if account is provided
    if account:
        session_name = f"aws-co-config-{os.getpid() % 10000}"
        
        if saas_account:
            click.echo(f"Testing role chaining...")
            click.echo(f"First assuming role {saas_role} in SaaS account {saas_account} using profile {source_profile}...")
            click.echo(f"Then assuming role {role} in target account {account}...")
            assume_role(account, "default", role, session_name, source_profile, saas_account, saas_role)
        else:
            click.echo(f"Assuming role {role} in account {account} using profile {DEFAULT_SOURCE_PROFILE}...")
            assume_role(account, DEFAULT_SOURCE_PROFILE, role, session_name)
        
        # Update recent accounts
        update_recent_accounts(config, account)
    
    if set_role:
        config["default_role"] = set_role
        click.echo(f"Default role set to: {set_role}")
    
    if set_saas_role:
        config["default_saas_role"] = set_saas_role
        click.echo(f"Default SaaS role set to: {set_saas_role}")
    
    if set_source_profile:
        config["default_source_profile"] = set_source_profile
        click.echo(f"Default source profile set to: {set_source_profile}")
    
    if set_role or set_saas_role or set_source_profile:
        save_config(config)
    
    # Display current config
    click.echo("\nCurrent configuration:")
    click.echo(f"Default role: {config.get('default_role', DEFAULT_ROLE)}")
    click.echo(f"Default SaaS role: {config.get('default_saas_role', DEFAULT_SAAS_ROLE)}")
    click.echo(f"Default source profile: {config.get('default_source_profile', DEFAULT_SOURCE_PROFILE)}")
    
    if "saas_account" in config:
        click.echo(f"SaaS account: {config['saas_account']}")
    
    if "default_target" in config:
        click.echo(f"Default target account: {config['default_target']}")
