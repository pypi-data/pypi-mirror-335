#!/usr/bin/env python3
"""
Configuration management for aws-co.
"""

import json
import logging
from pathlib import Path

# Set up logging
logger = logging.getLogger('awsco.config')

# Default values
DEFAULT_PROFILE = "default"
DEFAULT_ROLE = "ESW-CO-PowerUser-P2"
DEFAULT_SAAS_ROLE = "ESW-CO-PowerUser-P2"
DEFAULT_SOURCE_PROFILE = "default"
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
                "default_role": DEFAULT_ROLE,
                "default_saas_role": DEFAULT_SAAS_ROLE,
                "default_source_profile": DEFAULT_SOURCE_PROFILE,
                "recent_accounts": []
            }
    else:
        return {
            "default_role": DEFAULT_ROLE,
            "default_saas_role": DEFAULT_SAAS_ROLE,
            "default_source_profile": DEFAULT_SOURCE_PROFILE,
            "recent_accounts": []
        }

def save_config(config):
    """Save configuration to config file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving config file: {e}")

def update_recent_accounts(config, account_id):
    """Update the list of recently used accounts."""
    if not account_id:
        return
    
    if "recent_accounts" not in config:
        config["recent_accounts"] = []
    
    if account_id in config["recent_accounts"]:
        config["recent_accounts"].remove(account_id)
    
    config["recent_accounts"].insert(0, account_id)
    config["recent_accounts"] = config["recent_accounts"][:5]  # Keep only 5 most recent
    
    save_config(config)
