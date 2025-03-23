#!/usr/bin/env python3
"""
AWS commands for TPM-CLI.
"""

import os
import sys
import json
from tabulate import tabulate
from datetime import datetime
import aws_utils

def cmd_aws(args):
    """Handle AWS commands."""
    if not hasattr(args, 'subcommand') or not args.subcommand:
        print("Error: No subcommand specified for 'aws' command")
        print("Available subcommands: run, config, recent, setup, logs")
        sys.exit(1)
    
    if args.subcommand == 'run':
        cmd_aws_run(args)
    elif args.subcommand == 'config':
        cmd_aws_config(args)
    elif args.subcommand == 'recent':
        cmd_aws_recent(args)
    elif args.subcommand == 'setup':
        cmd_aws_setup(args)
    elif args.subcommand == 'logs':
        cmd_aws_logs(args)
    else:
        print(f"Error: Unknown subcommand '{args.subcommand}' for 'aws' command")
        sys.exit(1)

def cmd_aws_run(args):
    """Run AWS CLI commands with assumed role credentials."""
    try:
        # Load AWS configuration
        config = aws_utils.load_config()
        
        # Set up command parameters
        account = args.account
        role = args.role
        source_profile = args.source_profile
        saas_account = args.saas_account
        saas_role = args.saas_role
        debug = args.debug
        aws_args = args.aws_args
        
        # Use defaults from config if not specified
        if not account and 'target_account' in config:
            account = config['target_account']
        
        if not role and 'role' in config:
            role = config['role']
        
        if not source_profile and 'source_profile' in config:
            source_profile = config['source_profile']
        
        if not saas_account and 'saas_account' in config:
            saas_account = config['saas_account']
        
        if not saas_role and 'saas_role' in config:
            saas_role = config['saas_role']
        
        # Validate required parameters
        if not account:
            print("Error: Target AWS account ID is required. Specify with --account or set a default with 'aws config'.")
            sys.exit(1)
        
        if not aws_args:
            print("Error: No AWS CLI command specified. Please provide an AWS CLI command to run.")
            sys.exit(1)
        
        # Run AWS command
        result = aws_utils.run_aws_command(
            account=account,
            role=role,
            source_profile=source_profile,
            saas_account=saas_account,
            saas_role=saas_role,
            aws_args=aws_args,
            debug=debug
        )
        
        # Update recent accounts
        if account:
            aws_utils.update_recent_accounts(account)
        
        # Print result
        if result['stdout']:
            print(result['stdout'])
        
        if result['stderr']:
            print(result['stderr'], file=sys.stderr)
        
        sys.exit(result['returncode'])
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def cmd_aws_config(args):
    """Configure default settings for AWS."""
    try:
        # Load AWS configuration
        config = aws_utils.load_config()
        
        # Check if we're setting a default value
        if args.set_role:
            config['role'] = args.set_role
            print(f"Default role set to: {args.set_role}")
        
        if args.set_saas_role:
            config['saas_role'] = args.set_saas_role
            print(f"Default SaaS role set to: {args.set_saas_role}")
        
        if args.set_source_profile:
            config['source_profile'] = args.set_source_profile
            print(f"Default source profile set to: {args.set_source_profile}")
        
        # Test role assumption if account is specified
        if args.account:
            # Set up command parameters
            account = args.account
            role = args.role or config.get('role', 'OrganizationAccountAccessRole')
            source_profile = args.source_profile or config.get('source_profile')
            saas_account = args.saas_account or config.get('saas_account')
            saas_role = args.saas_role or config.get('saas_role')
            debug = args.debug
            
            # Test role assumption
            print(f"Testing role assumption for account {account}...")
            result = aws_utils.run_aws_command(
                account=account,
                role=role,
                source_profile=source_profile,
                saas_account=saas_account,
                saas_role=saas_role,
                aws_args=['sts', 'get-caller-identity'],
                debug=debug
            )
            
            if result['returncode'] == 0:
                print(f"Successfully assumed role in account {account}")
                print(result['stdout'])
                
                # Ask if user wants to set this as the default target account
                answer = input(f"Do you want to set {account} as your default target account? (y/n): ")
                if answer.lower() == 'y':
                    config['target_account'] = account
                    print(f"Default target account set to: {account}")
            else:
                print(f"Failed to assume role in account {account}")
                if result['stderr']:
                    print(result['stderr'], file=sys.stderr)
                sys.exit(1)
        
        # Save configuration
        aws_utils.save_config(config)
        
        # Display current configuration
        if not (args.set_role or args.set_saas_role or args.set_source_profile or args.account):
            print("Current AWS configuration:")
            print(f"Target Account: {config.get('target_account', 'Not set')}")
            print(f"Role: {config.get('role', 'Not set')}")
            print(f"Source Profile: {config.get('source_profile', 'Not set')}")
            print(f"SaaS Account: {config.get('saas_account', 'Not set')}")
            print(f"SaaS Role: {config.get('saas_role', 'Not set')}")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def cmd_aws_recent(args):
    """Show recently used AWS accounts."""
    try:
        # Load AWS configuration
        config = aws_utils.load_config()
        
        # Get recent accounts
        recent_accounts = config.get('recent_accounts', [])
        
        if not recent_accounts:
            print("No recently used accounts found.")
            sys.exit(0)
        
        # Display recent accounts
        print("Recently used AWS accounts:")
        table_data = []
        
        for i, account in enumerate(recent_accounts, 1):
            table_data.append([i, account])
        
        headers = ["#", "Account ID"]
        table = tabulate(table_data, headers=headers, tablefmt="grid")
        print(table)
        
        # Test role assumption if account is specified
        if args.account:
            # Set up command parameters
            account = args.account
            role = args.role or config.get('role', 'OrganizationAccountAccessRole')
            source_profile = args.source_profile or config.get('source_profile')
            saas_account = args.saas_account or config.get('saas_account')
            debug = args.debug
            
            # Test role assumption
            print(f"Testing role assumption for account {account}...")
            result = aws_utils.run_aws_command(
                account=account,
                role=role,
                source_profile=source_profile,
                saas_account=saas_account,
                aws_args=['sts', 'get-caller-identity'],
                debug=debug
            )
            
            if result['returncode'] == 0:
                print(f"Successfully assumed role in account {account}")
                print(result['stdout'])
            else:
                print(f"Failed to assume role in account {account}")
                if result['stderr']:
                    print(result['stderr'], file=sys.stderr)
                sys.exit(1)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def cmd_aws_setup(args):
    """Quick setup for SaaS and target accounts."""
    try:
        # Load AWS configuration
        config = aws_utils.load_config()
        
        # Set up command parameters
        saas_account = args.saas_account
        target_account = args.target_account
        role = args.role or config.get('role', 'OrganizationAccountAccessRole')
        saas_role = args.saas_role or config.get('saas_role', 'OrganizationAccountAccessRole')
        source_profile = args.source_profile or config.get('source_profile')
        debug = args.debug
        
        # Update configuration
        config['saas_account'] = saas_account
        if saas_role:
            config['saas_role'] = saas_role
        if source_profile:
            config['source_profile'] = source_profile
        
        print(f"SaaS account set to: {saas_account}")
        if saas_role:
            print(f"SaaS role set to: {saas_role}")
        if source_profile:
            print(f"Source profile set to: {source_profile}")
        
        # Test SaaS account access
        print(f"Testing access to SaaS account {saas_account}...")
        result = aws_utils.run_aws_command(
            account=saas_account,
            role=saas_role,
            source_profile=source_profile,
            aws_args=['sts', 'get-caller-identity'],
            debug=debug
        )
        
        if result['returncode'] != 0:
            print(f"Failed to assume role in SaaS account {saas_account}")
            if result['stderr']:
                print(result['stderr'], file=sys.stderr)
            sys.exit(1)
        
        print(f"Successfully accessed SaaS account {saas_account}")
        print(result['stdout'])
        
        # Test target account access if specified
        if target_account:
            print(f"Testing access to target account {target_account}...")
            result = aws_utils.run_aws_command(
                account=target_account,
                role=role,
                source_profile=source_profile,
                saas_account=saas_account,
                saas_role=saas_role,
                aws_args=['sts', 'get-caller-identity'],
                debug=debug
            )
            
            if result['returncode'] != 0:
                print(f"Failed to assume role in target account {target_account}")
                if result['stderr']:
                    print(result['stderr'], file=sys.stderr)
                sys.exit(1)
            
            print(f"Successfully accessed target account {target_account}")
            print(result['stdout'])
            
            # Set as default target account
            config['target_account'] = target_account
            print(f"Target account set to: {target_account}")
        
        # Save configuration
        aws_utils.save_config(config)
        
        print("Setup completed successfully.")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def cmd_aws_logs(args):
    """Get logs from CloudWatch Logs."""
    try:
        # Load AWS configuration
        config = aws_utils.load_config()
        
        # Set up command parameters
        account = args.account or config.get('target_account')
        role = args.role or config.get('role', 'OrganizationAccountAccessRole')
        source_profile = args.source_profile or config.get('source_profile')
        saas_account = args.saas_account or config.get('saas_account')
        saas_role = args.saas_role or config.get('saas_role')
        debug = args.debug
        
        # Validate required parameters
        if not account:
            print("Error: Target AWS account ID is required. Specify with --account or set a default with 'aws config'.")
            sys.exit(1)
        
        if not args.log_group:
            print("Error: Log group name is required.")
            sys.exit(1)
        
        # Prepare AWS CLI command for logs
        # Using sam logs instead of logs get-logs as per user preference
        aws_command = ['sam', 'logs', '--name', args.log_group]
        
        # Add optional parameters
        if args.start_time:
            aws_command.extend(['--start-time', args.start_time])
        
        if args.end_time:
            aws_command.extend(['--end-time', args.end_time])
        
        if args.filter_pattern:
            aws_command.extend(['--filter', args.filter_pattern])
        
        # Run AWS command
        result = aws_utils.run_aws_command(
            account=account,
            role=role,
            source_profile=source_profile,
            saas_account=saas_account,
            saas_role=saas_role,
            aws_args=aws_command,
            debug=debug
        )
        
        # Update recent accounts
        if account:
            aws_utils.update_recent_accounts(account)
        
        # Output logs
        if args.output:
            with open(args.output, 'w') as f:
                if result['stdout']:
                    f.write(result['stdout'])
                if result['stderr']:
                    f.write(result['stderr'])
            print(f"Logs saved to {args.output}")
        else:
            if result['stdout']:
                print(result['stdout'])
            
            if result['stderr']:
                print(result['stderr'], file=sys.stderr)
        
        sys.exit(result['returncode'])
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
