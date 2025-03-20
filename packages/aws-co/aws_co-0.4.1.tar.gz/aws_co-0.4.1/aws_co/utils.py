#!/usr/bin/env python3
"""
Utility functions for aws-co.
"""

import logging
import os
import signal
import subprocess
import sys

# Set up logging
logger = logging.getLogger('awsco.utils')

def handle_broken_pipe(*args):
    """
    Handle broken pipe errors gracefully.
    
    Python flushes standard streams on exit; redirect remaining output
    to /dev/null to avoid another BrokenPipeError at shutdown.
    """
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, sys.stdout.fileno())
    sys.exit(0)  # Exit with success code

def setup_signal_handlers():
    """Set up signal handlers for the application."""
    # Register the signal handler for broken pipes
    signal.signal(signal.SIGPIPE, handle_broken_pipe)

def check_aws_cli_installed():
    """Check if AWS CLI is installed and accessible."""
    try:
        subprocess.run(["aws", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_aws_profile(profile):
    """Check if an AWS profile exists and is configured correctly."""
    try:
        subprocess.run(
            ["aws", "sts", "get-caller-identity", "--profile", profile], 
            capture_output=True, 
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False
