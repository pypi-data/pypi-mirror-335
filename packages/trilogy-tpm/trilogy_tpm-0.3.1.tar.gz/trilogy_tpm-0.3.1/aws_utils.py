#!/usr/bin/env python3
"""
AWS utilities for TPM-CLI.
"""

import json
import logging
import os
import subprocess
import sys
from pathlib import Path

# Set up logging
logger = logging.getLogger('tpm.aws')
handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Default values
DEFAULT_PROFILE = "default"
DEFAULT_ROLE = "{TARGET_ROLE}"
DEFAULT_SAAS_ROLE = "{SAAS_ROLE}"
DEFAULT_SOURCE_PROFILE = "default"
CONFIG_FILE = Path.home() / ".tpm-cli" / "aws-config.json"

def setup_config_dir():
    """Set up the config directory if it doesn't exist."""
    config_dir = Path.home() / ".tpm-cli"
    if not config_dir.exists():
        config_dir.mkdir(parents=True, exist_ok=True)

def load_config():
    """Load configuration from config file."""
    setup_config_dir()
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
    setup_config_dir()
    # Create a backup of the existing config file if it exists
    if CONFIG_FILE.exists():
        backup_file = CONFIG_FILE.with_suffix('.json.bak')
        try:
            with open(CONFIG_FILE, 'r') as src, open(backup_file, 'w') as dst:
                dst.write(src.read())
            logger.debug(f"Created backup of config file at {backup_file}")
        except Exception as e:
            logger.error(f"Error creating backup of config file: {e}")
    
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving config file: {e}")

def update_recent_accounts(account_id=None, account=None):
    """
    Update the list of recently used accounts.
    
    Args:
        account_id (str): The AWS account ID to add to recent accounts
        account (str): Alternative parameter name for account_id
    """
    # Handle the alternative parameter name
    if account and not account_id:
        account_id = account
        
    if not account_id:
        return
    
    # Load config
    config = load_config()
    
    if "recent_accounts" not in config:
        config["recent_accounts"] = []
    
    if account_id in config["recent_accounts"]:
        config["recent_accounts"].remove(account_id)
    
    config["recent_accounts"].insert(0, account_id)
    config["recent_accounts"] = config["recent_accounts"][:5]  # Keep only 5 most recent
    
    save_config(config)

def check_aws_cli_installed():
    """Check if AWS CLI is installed."""
    try:
        subprocess.run(["aws", "--version"], capture_output=True, check=False)
        return True
    except FileNotFoundError:
        return False

def check_aws_profile(profile):
    """Check if AWS profile exists and is configured correctly."""
    try:
        result = subprocess.run(
            ["aws", "sts", "get-caller-identity", "--profile", profile],
            capture_output=True,
            check=False
        )
        return result.returncode == 0
    except Exception:
        return False

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
            raise Exception(f"Failed to assume role: {error_output}")
        except json.JSONDecodeError:
            logger.error("Error parsing AWS credentials")
            raise Exception("Failed to parse AWS credentials")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise Exception(f"Unexpected error: {e}")
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
            raise Exception(f"Failed to assume role: {error_output}")
        except json.JSONDecodeError:
            logger.error("Error parsing AWS credentials")
            raise Exception("Failed to parse AWS credentials")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise Exception(f"Unexpected error: {e}")

def run_aws_command(account_id=None, profile=None, role_name=None, aws_args=None, source_profile=None, saas_account=None, saas_role=None, debug=False, account=None, role=None):
    """
    Run an AWS command with assumed role credentials.
    
    Args:
        account_id (str): The AWS account ID to assume a role in
        account (str): Alternative parameter name for account_id
        profile (str): The AWS profile to use for assuming the role
        role_name (str): The name of the role to assume
        role (str): Alternative parameter name for role_name
        aws_args (list): The AWS command and arguments to run
        source_profile (str, optional): The source profile for role chaining
        saas_account (str, optional): The SaaS account ID for role chaining
        saas_role (str, optional): The SaaS role name for role chaining
        debug (bool, optional): Enable debug logging
    """
    # Handle the alternative parameter names
    if account and not account_id:
        account_id = account
    
    if role and not role_name:
        role_name = role
    
    if not aws_args:
        logger.error("No AWS command specified")
        return {"stdout": "", "stderr": "No AWS command specified", "returncode": 1}
    
    session_name = f"tpm-cli-{os.getpid() % 10000}"
    
    try:
        # Assume role and get credentials
        if saas_account and saas_role:
            logger.debug(f"Using role chaining with source profile: {source_profile}")
            credentials = assume_role(account_id, "default", role_name, session_name, source_profile, saas_account, saas_role)
        else:
            credentials = assume_role(account_id, profile or "default", role_name, session_name)
        
        # Prepare AWS command
        aws_cmd = ["aws"] + list(aws_args)
        
        # Set up environment with credentials
        env = os.environ.copy()
        env.update(credentials)
        
        # Run AWS command
        if debug:
            logger.debug(f"Running AWS command: {' '.join(aws_cmd)}")
        
        process = subprocess.Popen(
            aws_cmd, 
            env=env, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        
        return {"stdout": stdout, "stderr": stderr, "returncode": process.returncode}
    except Exception as e:
        error_msg = f"Error running AWS command: {e}"
        logger.error(error_msg)
        return {"stdout": "", "stderr": error_msg, "returncode": 1}

def get_logs(log_group, start_time=None, end_time=None, filter_pattern=None, account_id=None, role=None, source_profile=None, saas_account=None, saas_role=None):
    """
    Get logs from CloudWatch Logs.
    
    Args:
        log_group (str): The name of the log group
        start_time (str, optional): The start time in ISO format
        end_time (str, optional): The end time in ISO format
        filter_pattern (str, optional): The filter pattern
        account_id (str, optional): The AWS account ID to assume a role in
        role (str, optional): The name of the role to assume
        source_profile (str, optional): The source profile for role chaining
        saas_account (str, optional): The SaaS account ID for role chaining
        saas_role (str, optional): The SaaS role name for role chaining
        
    Returns:
        list: A list of log events
    """
    config = load_config()
    
    # Set defaults from config if not provided
    role = role or config.get("default_role", DEFAULT_ROLE)
    saas_role = saas_role or config.get("default_saas_role", DEFAULT_SAAS_ROLE)
    source_profile = source_profile or config.get("default_source_profile", DEFAULT_SOURCE_PROFILE)
    saas_account = saas_account or config.get("saas_account")
    
    # If account not provided, use default target
    if not account_id:
        account_id = config.get("default_target")
        if not account_id:
            logger.error("No account specified and no default target set.")
            return []
    
    # Prepare AWS command
    aws_cmd = ["logs", "filter-log-events", "--log-group-name", log_group]
    
    if start_time:
        aws_cmd.extend(["--start-time", start_time])
    
    if end_time:
        aws_cmd.extend(["--end-time", end_time])
    
    if filter_pattern:
        aws_cmd.extend(["--filter-pattern", filter_pattern])
    
    # Run AWS command
    session_name = f"tpm-cli-logs-{os.getpid() % 10000}"
    
    try:
        # Assume role and get credentials
        if saas_account and saas_role:
            logger.debug(f"Using role chaining with source profile: {source_profile}")
            credentials = assume_role(account_id, "default", role, session_name, source_profile, saas_account, saas_role)
        else:
            credentials = assume_role(account_id, source_profile, role, session_name)
        
        # Prepare AWS command
        aws_cmd = ["aws"] + aws_cmd + ["--output", "json"]
        
        # Set up environment with credentials
        env = os.environ.copy()
        env.update(credentials)
        
        # Run AWS command
        logger.debug(f"Running AWS command: {' '.join(aws_cmd)}")
        result = subprocess.run(aws_cmd, env=env, capture_output=True, text=True, check=True)
        
        # Parse JSON output
        events = json.loads(result.stdout).get("events", [])
        return events
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        return []
