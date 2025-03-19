#!/usr/bin/env python3
"""
CloudWatch Log Retention Savings Analyzer

This script analyzes AWS CloudWatch log groups across accounts to estimate
potential cost savings from implementing retention policies.

Usage:
    python cloudwatch_retention_savings.py [--accounts ACCOUNT_ID [ACCOUNT_ID ...]]

If no accounts are specified, the script will use the default profile.
"""

import argparse
import json
import subprocess
import sys
from typing import Dict, List, Tuple, Any


def run_aws_command(command: str, account_id: str = None) -> Dict:
    """Run an AWS CLI command and return the JSON output."""
    if account_id:
        cmd = f"aws-co run --account {account_id} -- {command}"
    else:
        cmd = f"aws {command}"
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        output = result.stdout
        
        # Extract the JSON part from aws-co output if needed
        if account_id:
            # Skip the AWS CLI output header
            json_start = output.find("{")
            if json_start == -1:
                json_start = output.find("[")
            if json_start != -1:
                output = output[json_start:]
        
        return json.loads(output)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error: {e.stderr}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from command: {cmd}")
        print(f"Output: {output}")
        print(f"Error: {e}")
        return {}


def format_size(size_bytes: int) -> str:
    """Convert bytes to a human-readable format."""
    if size_bytes == 0:
        return "0 B"
    size_names = ("B", "KB", "MB", "GB", "TB", "PB")
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    return f"{size_bytes:.2f} {size_names[i]}"


def bytes_to_gb(bytes_value: int) -> float:
    """Convert bytes to gigabytes."""
    return bytes_value / (1024 * 1024 * 1024)


def analyze_account(account_id: str = None) -> Dict[str, Any]:
    """Analyze CloudWatch log groups for a single account."""
    print(f"Analyzing account: {account_id or 'default'}")
    
    # Get all log groups
    log_groups_data = run_aws_command("logs describe-log-groups", account_id)
    
    if not log_groups_data or "logGroups" not in log_groups_data:
        print(f"No log groups found for account {account_id or 'default'}")
        return {
            "total_gb": 0,
            "no_retention_gb": 0,
            "annual_cost_total": 0,
            "annual_cost_no_retention": 0,
            "savings": {days: 0 for days in [7, 14, 30, 60, 90, 180, 365]},
            "top_groups": []
        }
    
    # Calculate total bytes and bytes without retention
    total_bytes = 0
    bytes_without_retention = 0
    log_groups_without_retention = []
    
    for log_group in log_groups_data["logGroups"]:
        size_bytes = log_group.get("storedBytes", 0)
        total_bytes += size_bytes
        
        if "retentionInDays" not in log_group or log_group["retentionInDays"] is None:
            bytes_without_retention += size_bytes
            log_groups_without_retention.append((log_group["logGroupName"], size_bytes))
    
    # Sort log groups by size (largest first)
    log_groups_without_retention.sort(key=lambda x: x[1], reverse=True)
    
    # Convert bytes to GB for cost calculation
    total_gb = bytes_to_gb(total_bytes)
    no_retention_gb = bytes_to_gb(bytes_without_retention)
    
    # AWS CloudWatch Logs pricing: $0.03 per GB per month for storage
    storage_cost_per_gb_month = 0.03
    monthly_cost_total = total_gb * storage_cost_per_gb_month
    monthly_cost_no_retention = no_retention_gb * storage_cost_per_gb_month
    annual_cost_total = monthly_cost_total * 12
    annual_cost_no_retention = monthly_cost_no_retention * 12
    
    # Calculate potential savings with different retention policies
    retention_periods = [7, 14, 30, 60, 90, 180, 365]
    annual_savings = {}
    
    # Assume log data grows linearly and is evenly distributed over time
    # This is a simplification - actual savings would depend on log generation patterns
    for days in retention_periods:
        # Estimate what percentage of logs would be kept with this retention policy
        # Assuming current logs represent approximately 1 year of data
        kept_percentage = min(days / 365, 1.0)
        new_size_bytes = bytes_without_retention * kept_percentage
        new_size_gb = bytes_to_gb(new_size_bytes)
        new_monthly_cost = new_size_gb * storage_cost_per_gb_month
        annual_savings[days] = (monthly_cost_no_retention - new_monthly_cost) * 12
    
    return {
        "total_gb": total_gb,
        "no_retention_gb": no_retention_gb,
        "annual_cost_total": annual_cost_total,
        "annual_cost_no_retention": annual_cost_no_retention,
        "savings": annual_savings,
        "top_groups": [(name, size) for name, size in log_groups_without_retention[:10]]
    }


def print_account_analysis(account_id: str, data: Dict[str, Any]) -> None:
    """Print analysis results for a single account."""
    print(f"\nACCOUNT: {account_id or 'default'}")
    print("=" * 70)
    print(f"Total log storage: {format_size(data['total_gb'] * 1024 * 1024 * 1024)} ({data['total_gb']:.2f} GB)")
    
    if data['total_gb'] > 0:
        print(f"Log storage without retention policies: {format_size(data['no_retention_gb'] * 1024 * 1024 * 1024)} ({data['no_retention_gb']:.2f} GB)")
        print(f"Percentage of logs without retention: {(data['no_retention_gb'] / data['total_gb'] * 100):.2f}%")
        print(f"\nCurrent estimated annual cost for all logs: ${data['annual_cost_total']:.2f}")
        print(f"Current estimated annual cost for logs without retention: ${data['annual_cost_no_retention']:.2f}")
        
        print("\nEstimated ANNUAL savings with different retention policies:")
        print("=" * 60)
        print("Retention Period (days)      Estimated Annual Savings      Savings %")
        print("-" * 60)
        for days in sorted([7, 14, 30, 60, 90, 180, 365]):
            savings_percent = (data['savings'][days] / data['annual_cost_no_retention'] * 100) if data['annual_cost_no_retention'] > 0 else 0
            print(f"{days:<25} ${data['savings'][days]:.2f}               {savings_percent:.2f}%")
        print("=" * 60)
        
        if data['top_groups']:
            print("\nTop 10 largest log groups without retention policies:")
            print("=" * 80)
            print("Log Group Name                                                  Size")
            print("-" * 80)
            for name, size in data['top_groups']:
                print(f"{name:<60} {format_size(size)}")
            print("=" * 80)
    else:
        print("No log groups with significant storage found.")


def print_combined_results(accounts_data: Dict[str, Dict[str, Any]]) -> None:
    """Print combined results for all analyzed accounts."""
    if not accounts_data:
        print("No account data available.")
        return
    
    # Calculate combined totals
    combined_total_gb = sum(data["total_gb"] for data in accounts_data.values())
    combined_no_retention_gb = sum(data["no_retention_gb"] for data in accounts_data.values())
    combined_annual_cost_total = sum(data["annual_cost_total"] for data in accounts_data.values())
    combined_annual_cost_no_retention = sum(data["annual_cost_no_retention"] for data in accounts_data.values())
    combined_savings = {}
    for days in [7, 14, 30, 60, 90, 180, 365]:
        combined_savings[days] = sum(data["savings"][days] for data in accounts_data.values())
    
    # Print combined results
    print("\nCOMBINED RESULTS FOR ALL ACCOUNTS")
    print("=" * 70)
    print(f"Total log storage: {combined_total_gb:.2f} GB")
    print(f"Log storage without retention policies: {combined_no_retention_gb:.2f} GB")
    
    if combined_total_gb > 0:
        print(f"Percentage of logs without retention: {(combined_no_retention_gb / combined_total_gb * 100):.2f}%")
        print(f"\nCurrent estimated annual cost for all logs: ${combined_annual_cost_total:.2f}")
        print(f"Current estimated annual cost for logs without retention: ${combined_annual_cost_no_retention:.2f}")
        
        print("\nEstimated ANNUAL savings with different retention policies:")
        print("=" * 70)
        print("Retention Period (days)      Estimated Annual Savings      Savings %")
        print("-" * 70)
        for days in sorted([7, 14, 30, 60, 90, 180, 365]):
            savings_percent = (combined_savings[days] / combined_annual_cost_no_retention * 100) if combined_annual_cost_no_retention > 0 else 0
            print(f"{days:<25} ${combined_savings[days]:.2f}               {savings_percent:.2f}%")
        print("=" * 70)
    
    # Print comparison table
    print("\nCOMPARISON BY ACCOUNT")
    print("=" * 100)
    print("Account         Total Storage   No Retention    Annual Cost     7-day Savings   30-day Savings")
    print("-" * 100)
    for account, data in accounts_data.items():
        print(f"{account:<15} {data['total_gb']:.2f} GB        {data['no_retention_gb']:.2f} GB        ${data['annual_cost_total']:.2f}          ${data['savings'][7]:.2f}          ${data['savings'][30]:.2f}")
    print("=" * 100)


def main():
    parser = argparse.ArgumentParser(description='Analyze CloudWatch log retention savings.')
    parser.add_argument('--accounts', nargs='+', help='AWS account IDs to analyze')
    args = parser.parse_args()
    
    accounts_to_analyze = args.accounts if args.accounts else [None]  # Use default profile if no accounts specified
    accounts_data = {}
    
    for account_id in accounts_to_analyze:
        account_data = analyze_account(account_id)
        accounts_data[account_id or "default"] = account_data
        print_account_analysis(account_id or "default", account_data)
    
    if len(accounts_data) > 1:
        print_combined_results(accounts_data)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
