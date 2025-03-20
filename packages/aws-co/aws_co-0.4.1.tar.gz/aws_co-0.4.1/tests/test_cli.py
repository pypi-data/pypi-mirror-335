"""
Tests for the aws-co CLI.
"""

import os
import pytest
from click.testing import CliRunner
from awsco.aws_co.cli import cli

def test_cli_help():
    """Test that the CLI help command works."""
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'aws-co: Run AWS CLI commands with assumed role credentials' in result.output
