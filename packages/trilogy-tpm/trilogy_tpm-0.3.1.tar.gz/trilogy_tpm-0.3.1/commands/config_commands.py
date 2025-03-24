#!/usr/bin/env python3
"""
Configuration commands for TPM-CLI.
"""

import sys
import os
import click

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from config_utils import (
    show_config,
    configure_service
)

def cmd_config_show(args):
    """Show the current configuration."""
    try:
        show_config()
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def cmd_config_google(args):
    """Configure Google Drive credentials."""
    try:
        if args.json_file:
            configure_service("google", json_file=args.json_file)
        else:
            print("Please provide a Google service account JSON file with --json-file.")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def cmd_config_github(args):
    """Configure GitHub credentials."""
    try:
        if args.token:
            configure_service("github", token=args.token)
        else:
            print("Please provide a GitHub token with --token.")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def cmd_config_jira(args):
    """Configure Jira credentials."""
    try:
        if args.email and args.token:
            configure_service("jira", email=args.email, token=args.token, server=args.server)
        else:
            print("Please provide both Jira email and token.")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def cmd_config_notion(args):
    """Configure Notion credentials."""
    try:
        if args.token:
            configure_service("notion", token=args.token)
        else:
            print("Please provide a Notion API token with --token.")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def cmd_config(args):
    """Handle config subcommands."""
    if args.config_action == "show":
        cmd_config_show(args)
    elif args.config_action == "google":
        cmd_config_google(args)
    elif args.config_action == "github":
        cmd_config_github(args)
    elif args.config_action == "jira":
        cmd_config_jira(args)
    elif args.config_action == "notion":
        cmd_config_notion(args)
    else:
        print("Please specify a valid config action.")
        sys.exit(1)
