#!/usr/bin/env python3
"""
Jira commands for TPM-CLI.
"""

import sys
import click
import os

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from jira_utils import (
    get_ticket, 
    search_tickets, 
    add_comment, 
    set_config,
    show_config
)

def cmd_jira_get(args):
    """Get a Jira ticket by its key."""
    try:
        get_ticket(
            ticket_key=args.ticket_key,
            output_format=args.format,
            output_file=args.output
        )
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def cmd_jira_search(args):
    """Search for Jira tickets using JQL."""
    try:
        search_tickets(
            query=args.query,
            limit=args.limit,
            output_format=args.format,
            output_file=args.output
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
