#!/usr/bin/env python3
"""
CloudTrail Optimization Analyzer

This script analyzes AWS CloudTrail usage across multiple accounts and provides
recommendations for optimization and cost savings.

Usage:
    python3 cloudtrail_optimization.py [--accounts ACCOUNT_ID [ACCOUNT_ID ...]]
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    print("tqdm not available. Install with 'pip install tqdm' for progress bars.")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Analyze CloudTrail usage and potential savings')
    parser.add_argument('--accounts', nargs='+', help='AWS account IDs to analyze')
    return parser.parse_args()


def run_aws_command(command, account_id=None):
    """Run an AWS CLI command and return the JSON output."""
    if account_id:
        cmd = f"aws-co run --account {account_id} -- {command}"
    else:
        cmd = f"aws {command}"
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        
        # Extract the JSON part from aws-co output if needed
        if account_id:
            # Find where the actual command output starts
            cmd_marker = f"Running: aws {command}"
            if cmd_marker in output:
                output = output[output.find(cmd_marker) + len(cmd_marker):].strip()
            
            # Try to find JSON content
            json_start = output.find("{")
            if json_start == -1:
                json_start = output.find("[")
            
            if json_start != -1:
                output = output[json_start:]
                
                # Handle potential trailing text after JSON
                json_end = None
                brace_count = 0
                bracket_count = 0
                in_string = False
                escape_next = False
                
                for i, char in enumerate(output):
                    if escape_next:
                        escape_next = False
                        continue
                        
                    if char == '\\':
                        escape_next = True
                    elif char == '"' and not escape_next:
                        in_string = not in_string
                    elif not in_string:
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0 and bracket_count == 0 and json_start == output.find("{"):
                                json_end = i + 1
                                break
                        elif char == '[':
                            bracket_count += 1
                        elif char == ']':
                            bracket_count -= 1
                            if bracket_count == 0 and brace_count == 0 and json_start == output.find("["):
                                json_end = i + 1
                                break
                
                if json_end:
                    output = output[:json_end]
        
        # Handle text output that might be a number
        output = output.strip()
        if output.isdigit():
            return int(output)
        
        # Try to parse as JSON
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            # If it's a text output with multiple lines, return as list
            if '\n' in output:
                return [line.strip() for line in output.split('\n') if line.strip()]
            return output
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error: {e.stderr}")
        return {}
    except json.JSONDecodeError:
        print(f"Error parsing JSON from command: {cmd}")
        print(f"Output: {output}")
        # If it looks like a number, try to return as int
        if output.strip().isdigit():
            return int(output.strip())
        # If it's a text output with multiple lines, return as list
        if '\n' in output:
            return [line.strip() for line in output.split('\n') if line.strip()]
        return output


def get_trail_size(account_id, trail_name, s3_bucket, s3_prefix=None):
    """Get the size of CloudTrail logs in S3."""
    prefix = f"{s3_prefix}/AWSLogs/{account_id}/CloudTrail" if s3_prefix else f"AWSLogs/{account_id}/CloudTrail"
    
    # Get the total size of CloudTrail logs in S3
    cmd = f"s3api list-objects-v2 --bucket {s3_bucket} --prefix {prefix} --query \"sum(Contents[].Size)\" --output json"
    try:
        result = run_aws_command(cmd, account_id)
        if result is not None and isinstance(result, (int, float)):
            return result
        return 0
    except:
        # If the command fails, try to get the size by listing objects
        try:
            cmd = f"s3api list-objects-v2 --bucket {s3_bucket} --prefix {prefix} --query \"Contents[].Size\" --output json"
            result = run_aws_command(cmd, account_id)
            if isinstance(result, list):
                return sum(result)
            return 0
        except:
            return 0


def get_cloudwatch_logs_size(account_id, log_group):
    """Get the size of CloudWatch logs."""
    cmd = f"logs describe-log-groups --log-group-name-prefix {log_group} --query \"logGroups[0].storedBytes\""
    try:
        result = run_aws_command(cmd, account_id)
        if result is not None:
            if isinstance(result, (int, float)):
                return result
            elif isinstance(result, str) and result.isdigit():
                return int(result)
        return 0
    except:
        return 0


def check_dependencies(account_id, trail_name):
    """Check for resources that depend on this CloudTrail."""
    dependencies = []
    
    # Check for CloudWatch Alarms that might be using CloudTrail
    try:
        alarms_cmd = f"cloudwatch describe-alarms"
        alarms = run_aws_command(alarms_cmd, account_id)
        
        if isinstance(alarms, dict) and "MetricAlarms" in alarms:
            cloudtrail_alarms = [
                alarm for alarm in alarms["MetricAlarms"] 
                if "CloudTrail" in alarm.get("AlarmName", "") or trail_name in alarm.get("AlarmName", "")
            ]
            
            for alarm in cloudtrail_alarms:
                dependencies.append({
                    "type": "CloudWatch Alarm",
                    "name": alarm.get("AlarmName", "Unknown"),
                    "description": f"CloudWatch Alarm that may be monitoring CloudTrail metrics"
                })
    except Exception as e:
        print(f"Error checking CloudWatch alarms: {str(e)}")
    
    # Check for Lambda functions that might be processing CloudTrail logs
    try:
        functions_cmd = f"lambda list-functions"
        functions = run_aws_command(functions_cmd, account_id)
        
        if isinstance(functions, dict) and "Functions" in functions:
            cloudtrail_functions = [
                func for func in functions["Functions"]
                if "CloudTrail" in func.get("FunctionName", "") or trail_name in func.get("FunctionName", "")
            ]
            
            for func in cloudtrail_functions:
                dependencies.append({
                    "type": "Lambda Function",
                    "name": func.get("FunctionName", "Unknown"),
                    "description": f"Lambda function that may be processing CloudTrail logs"
                })
    except Exception as e:
        print(f"Error checking Lambda functions: {str(e)}")
    
    # Check for EventBridge rules that might be using CloudTrail
    try:
        rules_cmd = f"events list-rules"
        rules = run_aws_command(rules_cmd, account_id)
        
        if isinstance(rules, dict) and "Rules" in rules:
            cloudtrail_rules = [
                rule for rule in rules["Rules"]
                if "CloudTrail" in rule.get("Name", "") or trail_name in rule.get("Name", "")
            ]
            
            for rule in cloudtrail_rules:
                dependencies.append({
                    "type": "EventBridge Rule",
                    "name": rule.get("Name", "Unknown"),
                    "description": f"EventBridge rule that may be triggered by CloudTrail events"
                })
    except Exception as e:
        print(f"Error checking EventBridge rules: {str(e)}")
    
    return dependencies


def analyze_cloudtrail(account_id):
    """Analyze CloudTrail usage and potential savings."""
    print(f"Analyzing CloudTrail for account: {account_id}")
    
    # Get all trails
    print("  Getting CloudTrail trails...")
    trails = run_aws_command("cloudtrail describe-trails", account_id)
    if not trails or "trailList" not in trails:
        print(f"No CloudTrail trails found for account {account_id}")
        return {
            "account_id": account_id,
            "trails": [],
            "total_s3_size_bytes": 0,
            "total_cloudwatch_size_bytes": 0,
            "monthly_cost": 0,
            "annual_cost": 0,
            "dependencies": []
        }
    
    trail_details = []
    total_s3_size = 0
    total_cloudwatch_size = 0
    all_dependencies = []
    
    trail_list = trails["trailList"]
    print(f"  Found {len(trail_list)} CloudTrail trails")
    
    # Create progress bar for trails
    if TQDM_AVAILABLE:
        trail_iter = tqdm(trail_list, desc="Analyzing trails", unit="trail")
    else:
        trail_iter = trail_list
    
    for trail in trail_iter:
        trail_name = trail["Name"]
        if not TQDM_AVAILABLE:
            print(f"  Analyzing trail: {trail_name}")
        
        # Get trail status
        if TQDM_AVAILABLE:
            trail_iter.set_description(f"Getting status for {trail_name}")
        else:
            print(f"    Getting status for {trail_name}...")
        status = run_aws_command(f"cloudtrail get-trail-status --name {trail_name}", account_id)
        is_logging = status.get("IsLogging", False)
        
        # Get event selectors
        if TQDM_AVAILABLE:
            trail_iter.set_description(f"Getting event selectors for {trail_name}")
        else:
            print(f"    Getting event selectors for {trail_name}...")
        selectors = run_aws_command(f"cloudtrail get-event-selectors --trail-name {trail_name}", account_id)
        event_selectors = selectors.get("EventSelectors", [])
        
        # Calculate S3 storage size
        s3_bucket = trail.get("S3BucketName")
        s3_prefix = trail.get("S3KeyPrefix", "")
        s3_size = 0
        if s3_bucket:
            if TQDM_AVAILABLE:
                trail_iter.set_description(f"Calculating S3 storage for {trail_name}")
            else:
                print(f"    Calculating S3 storage for {trail_name}...")
            s3_size = get_trail_size(account_id, trail_name, s3_bucket, s3_prefix)
            total_s3_size += s3_size
        
        # Calculate CloudWatch Logs size
        cloudwatch_log_group = None
        cloudwatch_size = 0
        if "CloudWatchLogsLogGroupArn" in trail:
            if TQDM_AVAILABLE:
                trail_iter.set_description(f"Calculating CloudWatch Logs storage for {trail_name}")
            else:
                print(f"    Calculating CloudWatch Logs storage for {trail_name}...")
            cloudwatch_log_group = trail["CloudWatchLogsLogGroupArn"].split(":log-group:")[1].split(":")[0]
            cloudwatch_size = get_cloudwatch_logs_size(account_id, cloudwatch_log_group)
            total_cloudwatch_size += cloudwatch_size
        
        # Check for dependencies
        dependencies = []
        if "IsOrganizationTrail" in trail and trail["IsOrganizationTrail"]:
            dependencies.append({
                "type": "Organization",
                "name": "AWS Organization",
                "description": "This is an organization trail that logs events for all AWS accounts in the organization."
            })
        
        # Check for other dependencies
        if TQDM_AVAILABLE:
            trail_iter.set_description(f"Checking dependencies for {trail_name}")
        else:
            print(f"    Checking dependencies for {trail_name}...")
        trail_dependencies = check_dependencies(account_id, trail_name)
        dependencies.extend(trail_dependencies)
        all_dependencies.extend(dependencies)
        
        # Add trail details
        trail_details.append({
            "name": trail_name,
            "is_logging": is_logging,
            "is_multi_region": trail.get("IsMultiRegionTrail", False),
            "is_organization_trail": trail.get("IsOrganizationTrail", False),
            "s3_bucket": s3_bucket,
            "s3_prefix": s3_prefix,
            "s3_size_bytes": s3_size,
            "cloudwatch_log_group": cloudwatch_log_group,
            "cloudwatch_size_bytes": cloudwatch_size,
            "event_selectors": event_selectors,
            "created_time": status.get("StartLoggingTime", ""),
            "dependencies": dependencies
        })
    
    # Calculate costs
    print("  Calculating costs...")
    # CloudTrail pricing: $2 per million events (management events)
    # S3 pricing: $0.023 per GB per month
    # CloudWatch Logs pricing: $0.03 per GB per month for storage
    s3_cost_per_gb_month = 0.023
    cloudwatch_cost_per_gb_month = 0.03
    
    s3_size_gb = total_s3_size / (1024 * 1024 * 1024) if total_s3_size > 0 else 0
    cloudwatch_size_gb = total_cloudwatch_size / (1024 * 1024 * 1024) if total_cloudwatch_size > 0 else 0
    
    monthly_s3_cost = s3_size_gb * s3_cost_per_gb_month
    monthly_cloudwatch_cost = cloudwatch_size_gb * cloudwatch_cost_per_gb_month
    monthly_cost = monthly_s3_cost + monthly_cloudwatch_cost
    annual_cost = monthly_cost * 12
    
    return {
        "account_id": account_id,
        "trails": trail_details,
        "total_s3_size_bytes": total_s3_size,
        "total_cloudwatch_size_bytes": total_cloudwatch_size,
        "monthly_cost": monthly_cost,
        "annual_cost": annual_cost,
        "dependencies": all_dependencies
    }


def format_size(size_bytes):
    """Convert bytes to a human-readable format."""
    if size_bytes == 0:
        return "0 B"
    size_names = ("B", "KB", "MB", "GB", "TB", "PB")
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    return f"{size_bytes:.2f} {size_names[i]}"


def print_analysis(analysis):
    """Print the CloudTrail analysis results."""
    account_id = analysis["account_id"]
    trails = analysis["trails"]
    
    print(f"\nCLOUDTRAIL ANALYSIS FOR ACCOUNT: {account_id}")
    print("=" * 80)
    
    if not trails:
        print("No CloudTrail trails found.")
        return
    
    print(f"Number of trails: {len(trails)}")
    print(f"Total S3 storage: {format_size(analysis['total_s3_size_bytes'])}")
    print(f"Total CloudWatch Logs storage: {format_size(analysis['total_cloudwatch_size_bytes'])}")
    print(f"Estimated monthly cost: ${analysis['monthly_cost']:.2f}")
    print(f"Estimated annual cost: ${analysis['annual_cost']:.2f}")
    
    print("\nTrail Details:")
    print("-" * 80)
    for trail in trails:
        print(f"Name: {trail['name']}")
        print(f"  Status: {'Active' if trail['is_logging'] else 'Inactive'}")
        print(f"  Multi-region: {'Yes' if trail['is_multi_region'] else 'No'}")
        print(f"  Organization trail: {'Yes' if trail['is_organization_trail'] else 'No'}")
        print(f"  S3 bucket: {trail['s3_bucket']}")
        print(f"  S3 storage: {format_size(trail['s3_size_bytes'])}")
        if trail['cloudwatch_log_group']:
            print(f"  CloudWatch Log Group: {trail['cloudwatch_log_group']}")
            print(f"  CloudWatch Logs storage: {format_size(trail['cloudwatch_size_bytes'])}")
        
        # Event selectors
        if trail["event_selectors"]:
            print("  Event Selectors:")
            for selector in trail["event_selectors"]:
                read_write = selector.get("ReadWriteType", "Unknown")
                include_mgmt = selector.get("IncludeManagementEvents", False)
                print(f"    - Read/Write: {read_write}, Management Events: {'Yes' if include_mgmt else 'No'}")
        
        # Dependencies
        if trail["dependencies"]:
            print("  Dependencies:")
            for dep in trail["dependencies"]:
                print(f"    - Type: {dep['type']}, Name: {dep['name']}")
        
        print("-" * 40)
    
    print("\nRecommendations:")
    print("-" * 80)
    
    # Generate recommendations
    if len(trails) > 1:
        print("- Consider consolidating multiple trails into a single trail to reduce costs.")
    
    for trail in trails:
        if trail["is_logging"] and trail["event_selectors"]:
            for selector in trail["event_selectors"]:
                if selector.get("ReadWriteType", "") == "All" and selector.get("IncludeManagementEvents", False):
                    print(f"- For trail '{trail['name']}', consider logging only 'Write' management events instead of 'All' to reduce volume.")
    
    # CloudWatch Logs recommendations
    if analysis["total_cloudwatch_size_bytes"] > 0:
        print("- Implement a 30-day retention policy for CloudWatch Logs to reduce storage costs.")
    
    print("- Regularly clean up old CloudTrail logs in S3 using lifecycle policies.")
    
    # Calculate potential savings
    potential_savings = 0
    
    # Savings from consolidating trails
    if len(trails) > 1:
        # Assume 20% savings from consolidation
        potential_savings += analysis["annual_cost"] * 0.2
    
    # Savings from logging only write events
    # Assume 60% of events are read events
    potential_savings += analysis["annual_cost"] * 0.6 * 0.5  # 50% of the 60% read events
    
    # Savings from CloudWatch Logs retention
    if analysis["total_cloudwatch_size_bytes"] > 0:
        # Assume 70% savings from 30-day retention
        potential_savings += (analysis["total_cloudwatch_size_bytes"] / (analysis["total_s3_size_bytes"] + analysis["total_cloudwatch_size_bytes"] or 1)) * analysis["annual_cost"] * 0.7
    
    print(f"\nEstimated annual savings from all recommendations: ${potential_savings:.2f}")
    print("=" * 80)


def can_delete_trail(trail):
    """Determine if a trail can be safely deleted."""
    # Check if it's an organization trail
    if trail["is_organization_trail"]:
        return False, "This is an organization trail and should not be deleted."
    
    # Check for dependencies
    if trail["dependencies"]:
        return False, f"This trail has {len(trail['dependencies'])} dependencies."
    
    # Check if it's a default trail created by AWS services
    if "aws-controltower" in trail["name"] or "Default" == trail["name"]:
        return False, "This appears to be a default trail created by AWS services."
    
    return True, "This trail appears to be safe to delete."


def print_combined_results(results):
    """Print combined results for all accounts."""
    total_s3_size = sum(analysis["total_s3_size_bytes"] for analysis in results.values())
    total_cloudwatch_size = sum(analysis["total_cloudwatch_size_bytes"] for analysis in results.values())
    total_monthly_cost = sum(analysis["monthly_cost"] for analysis in results.values())
    total_annual_cost = sum(analysis["annual_cost"] for analysis in results.values())
    
    print("\nCOMBINED RESULTS FOR ALL ACCOUNTS")
    print("=" * 80)
    print(f"Total S3 storage: {format_size(total_s3_size)}")
    print(f"Total CloudWatch Logs storage: {format_size(total_cloudwatch_size)}")
    print(f"Total estimated monthly cost: ${total_monthly_cost:.2f}")
    print(f"Total estimated annual cost: ${total_annual_cost:.2f}")
    
    # Calculate total potential savings
    total_potential_savings = 0
    for account_id, analysis in results.items():
        # Savings from consolidating trails
        if len(analysis["trails"]) > 1:
            total_potential_savings += analysis["annual_cost"] * 0.2
        
        # Savings from logging only write events
        total_potential_savings += analysis["annual_cost"] * 0.6 * 0.5
        
        # Savings from CloudWatch Logs retention
        if analysis["total_cloudwatch_size_bytes"] > 0:
            total_potential_savings += (analysis["total_cloudwatch_size_bytes"] / (analysis["total_s3_size_bytes"] + analysis["total_cloudwatch_size_bytes"] or 1)) * analysis["annual_cost"] * 0.7
    
    print(f"Total estimated annual savings from all recommendations: ${total_potential_savings:.2f}")
    
    # Print deletion recommendations
    print("\nDELETION RECOMMENDATIONS")
    print("-" * 80)
    for account_id, analysis in results.items():
        for trail in analysis["trails"]:
            can_delete, reason = can_delete_trail(trail)
            if can_delete:
                print(f"Account {account_id}, Trail '{trail['name']}' can potentially be deleted.")
                print(f"  Reason: {reason}")
                print(f"  Estimated annual savings: ${(trail['s3_size_bytes'] / (analysis['total_s3_size_bytes'] or 1)) * analysis['annual_cost']:.2f}")
            else:
                print(f"Account {account_id}, Trail '{trail['name']}' should NOT be deleted.")
                print(f"  Reason: {reason}")
            print("-" * 40)
    
    print("\nGENERAL RECOMMENDATIONS")
    print("-" * 80)
    print("1. Consolidate trails: If multiple trails exist across accounts, consider using organization trails.")
    print("2. Optimize event logging: Log only write events instead of all events to reduce volume.")
    print("3. Implement retention policies: Set up lifecycle policies for S3 and retention for CloudWatch Logs.")
    print("4. Regular cleanup: Schedule regular cleanup of old CloudTrail logs.")
    print("5. Cost monitoring: Regularly monitor CloudTrail costs to identify unexpected increases.")
    print("=" * 80)


def main():
    """Main function."""
    args = parse_args()
    
    # If no accounts specified, try to get the current account
    if not args.accounts:
        try:
            print("No account specified. Attempting to determine current account...")
            current = run_aws_command("sts get-caller-identity --query Account --output text")
            if current:
                accounts = [current]
                print(f"Using current account: {current}")
            else:
                print("Error: No account specified and unable to determine current account.")
                sys.exit(1)
        except Exception as e:
            print(f"Error determining current account: {e}")
            print("Please specify one or more account IDs using the --accounts option.")
            sys.exit(1)
    else:
        accounts = args.accounts
    
    results = {}
    
    # Create progress bar for accounts
    if TQDM_AVAILABLE and len(accounts) > 1:
        account_iter = tqdm(accounts, desc="Analyzing accounts", unit="account")
    else:
        account_iter = accounts
    
    for account_id in account_iter:
        if TQDM_AVAILABLE and len(accounts) > 1:
            account_iter.set_description(f"Analyzing account {account_id}")
        
        results[account_id] = analyze_cloudtrail(account_id)
        print_analysis(results[account_id])
    
    if len(accounts) > 1:
        print_combined_results(results)


if __name__ == "__main__":
    main()
