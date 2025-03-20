"""
Command modules for aws-co CLI.
"""

from .run import run_command
from .config import config_command
from .recent import recent_command
from .setup import setup_command

__all__ = [
    'run_command',
    'config_command',
    'recent_command',
    'setup_command'
]
