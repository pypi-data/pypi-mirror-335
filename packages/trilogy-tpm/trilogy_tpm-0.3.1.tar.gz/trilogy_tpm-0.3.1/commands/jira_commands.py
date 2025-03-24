#!/usr/bin/env python3
"""
Jira commands for TPM-CLI.
"""

import sys
import argparse
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jira_utils import (
    get_ticket, 
    get_ticket_direct, 
    search_tickets, 
    add_comment, 
    set_config,
    get_jira_credentials,
    test_jira_connection,
    list_jira_projects
)

def cmd_jira_get(args):
    """Get a Jira ticket by its key."""
    try:
        # Try the direct HTTP request method first
        get_ticket_direct(
            ticket_key=args.issue_key,
            output_format=getattr(args, 'format', 'md'),
            output_file=getattr(args, 'output', None)
        )
    except Exception as e:
        print(f"Direct HTTP request failed: {str(e)}")
        print("Falling back to JIRA library method...")
        try:
            # Fall back to the JIRA library method
            get_ticket(
                ticket_key=args.issue_key,
                output_format=getattr(args, 'format', 'md'),
                output_file=getattr(args, 'output', None)
            )
        except Exception as e:
            print(f"Error: {str(e)}")
            print("\nTroubleshooting tips:")
            print("1. Your API token may not have permission to access this ticket")
            print("2. You can still access the ticket in your web browser at:")
            print(f"   https://trilogy-eng.atlassian.net/browse/{args.issue_key}")
            print("3. To update your Jira API token, run: tpm config jira --email <email> --token <token>")
            print("4. To check your Jira connection, run: tpm jira test")
            sys.exit(1)

def cmd_jira_search(args):
    """Search for Jira tickets using JQL."""
    try:
        search_tickets(
            query=args.query,
            limit=getattr(args, 'limit', 10),
            output_format=getattr(args, 'format', 'md'),
            output_file=getattr(args, 'output', None)
        )
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def cmd_jira_comment(args):
    """Add a comment to a Jira ticket."""
    try:
        add_comment(
            ticket_key=args.ticket_key,
            comment_text=args.comment
        )
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def cmd_jira_config(args):
    """Set or show Jira configuration."""
    try:
        if args.email or args.token:
            set_config(
                email=args.email,
                token=args.token
            )
        else:
            show_config()
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def cmd_jira_test(args):
    """Test the Jira connection."""
    test_jira_connection()

def cmd_jira_projects(args):
    """List all accessible Jira projects."""
    list_jira_projects()

def cmd_jira(args):
    """Handle Jira subcommands."""
    if args.subcommand == 'get':
        cmd_jira_get(args)
    elif args.subcommand == 'search':
        cmd_jira_search(args)
    elif args.subcommand == 'comment':
        cmd_jira_comment(args)
    elif args.subcommand == 'config':
        cmd_jira_config(args)
    elif args.subcommand == 'test':
        cmd_jira_test(args)
    elif args.subcommand == 'projects':
        cmd_jira_projects(args)
