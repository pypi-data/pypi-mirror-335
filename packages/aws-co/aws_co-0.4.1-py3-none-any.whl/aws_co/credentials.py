#!/usr/bin/env python3
"""
AWS credential management and role assumption for aws-co.
"""

import json
import logging
import os
import subprocess
import sys
import click

from .config import DEFAULT_PROFILE, DEFAULT_SOURCE_PROFILE

# Set up logging
logger = logging.getLogger('awsco.credentials')

def assume_role(account_id, profile, role_name, session_name, source_profile=None, saas_account=None, saas_role=None):
    """
    Assume the specified role and return credentials.
    
    If saas_account and saas_role are provided, this will:
    1. Assume the saas_role in saas_account using source_profile
    2. Then assume the role_name in account_id using the credentials from step 1
    
    Args:
        account_id (str): The AWS account ID to assume a role in
        profile (str): The AWS profile to use for assuming the role
        role_name (str): The name of the role to assume
        session_name (str): The session name for the assumed role
        source_profile (str, optional): The source profile for role chaining
        saas_account (str, optional): The SaaS account ID for role chaining
        saas_role (str, optional): The SaaS role name for role chaining
        
    Returns:
        dict: A dictionary with AWS credentials environment variables
    """
    if saas_account and saas_role:
        # Step 1: Assume role in SaaS account
        source_profile = source_profile or DEFAULT_SOURCE_PROFILE
        logger.debug(f"Using source profile {source_profile} to assume role {saas_role} in SaaS account {saas_account}")
        
        saas_cmd = [
            "aws", "sts", "assume-role",
            "--role-arn", f"arn:aws:iam::{saas_account}:role/{saas_role}",
            "--role-session-name", f"{session_name}-saas",
            "--profile", source_profile,
            "--output", "json"
        ]
        
        try:
            logger.debug(f"Running command: {' '.join(saas_cmd)}")
            saas_result = subprocess.run(saas_cmd, capture_output=True, check=True, text=True)
            saas_credentials = json.loads(saas_result.stdout)["Credentials"]
            
            # Step 2: Assume role in target account using SaaS credentials
            target_cmd = [
                "aws", "sts", "assume-role",
                "--role-arn", f"arn:aws:iam::{account_id}:role/{role_name}",
                "--role-session-name", session_name,
                "--output", "json"
            ]
            
            env = os.environ.copy()
            env["AWS_ACCESS_KEY_ID"] = saas_credentials["AccessKeyId"]
            env["AWS_SECRET_ACCESS_KEY"] = saas_credentials["SecretAccessKey"]
            env["AWS_SESSION_TOKEN"] = saas_credentials["SessionToken"]
            
            logger.debug(f"Running command: {' '.join(target_cmd)}")
            target_result = subprocess.run(target_cmd, capture_output=True, check=True, text=True, env=env)
            target_credentials = json.loads(target_result.stdout)["Credentials"]
            
            return {
                "AWS_ACCESS_KEY_ID": target_credentials["AccessKeyId"],
                "AWS_SECRET_ACCESS_KEY": target_credentials["SecretAccessKey"],
                "AWS_SESSION_TOKEN": target_credentials["SessionToken"]
            }
            
        except subprocess.CalledProcessError as e:
            error_output = e.stderr.strip() if e.stderr else "Unknown error"
            logger.error(f"Error assuming role: {error_output}")
            raise click.ClickException(f"Failed to assume role: {error_output}")
        except json.JSONDecodeError:
            logger.error("Error parsing AWS credentials")
            raise click.ClickException("Failed to parse AWS credentials")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise click.ClickException(f"Unexpected error: {e}")
    else:
        # Direct role assumption
        cmd = [
            "aws", "sts", "assume-role",
            "--role-arn", f"arn:aws:iam::{account_id}:role/{role_name}",
            "--role-session-name", session_name,
            "--profile", profile,
            "--output", "json"
        ]
        
        try:
            logger.debug(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, check=True, text=True)
            credentials = json.loads(result.stdout)["Credentials"]
            
            return {
                "AWS_ACCESS_KEY_ID": credentials["AccessKeyId"],
                "AWS_SECRET_ACCESS_KEY": credentials["SecretAccessKey"],
                "AWS_SESSION_TOKEN": credentials["SessionToken"]
            }
            
        except subprocess.CalledProcessError as e:
            error_output = e.stderr.strip() if e.stderr else "Unknown error"
            logger.error(f"Error assuming role: {error_output}")
            raise click.ClickException(f"Failed to assume role: {error_output}")
        except json.JSONDecodeError:
            logger.error("Error parsing AWS credentials")
            raise click.ClickException("Failed to parse AWS credentials")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise click.ClickException(f"Unexpected error: {e}")

def run_aws_command(account_id, profile, role_name, aws_args, source_profile=None, saas_account=None, saas_role=None):
    """Run an AWS command with assumed role credentials."""
    session_name = f"aws-co-session-{os.getpid() % 10000}"
    
    if saas_account and saas_role:
        click.echo(f"Assuming role {saas_role} in SaaS account {saas_account}...")
        click.echo(f"Then assuming role {role_name} in target account {account_id}...")
    else:
        click.echo(f"Assuming role {role_name} in account {account_id} using profile {profile}...")
    
    # Assume the role
    credentials = assume_role(
        account_id, 
        profile, 
        role_name, 
        session_name, 
        source_profile, 
        saas_account, 
        saas_role
    )
    
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
