#!/usr/bin/env python3
"""
aws-co: A wrapper for AWS CLI that assumes a role before running commands.
"""

import sys
import logging
import click

from .utils import setup_signal_handlers
from .commands import (
    run_command,
    config_command,
    recent_command,
    setup_command
)

# Set up logging
logger = logging.getLogger('awsco')
handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Set up signal handlers
setup_signal_handlers()

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
