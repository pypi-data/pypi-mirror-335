#!/usr/bin/env python3
"""
TPM-CLI: A command-line tool for interacting with GitHub repositories, Google Drive documents, AWS services, Jira, and Notion.
"""

import argparse
import os
import sys
import importlib.util
import inspect

# Add the current directory to the path so we can import the command modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import command modules
from commands import github_commands, google_commands, aws_commands, jira_commands, config_commands, notion_commands

VERSION = "0.3.0"

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description='TPM CLI - Tools for Technical Project Managers')
    parser.add_argument('--version', action='version', version=f'TPM CLI v{VERSION}')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # GitHub repository command
    repo_parser = subparsers.add_parser('repo', help='Find repositories or get repository information')
    repo_parser.add_argument('query', help='Repository name or search query')
    repo_parser.add_argument('--org', help='GitHub organization')
    repo_parser.add_argument('--output', help='Output file path for markdown table')
    repo_parser.add_argument('--limit-pages', action='store_true', help='Limit the number of pages to fetch')
    repo_parser.add_argument('--max-pages', type=int, help='Maximum number of pages to fetch (default: all)')
    repo_parser.add_argument('--details', action='store_true', help='Show detailed information even when multiple results are found')
    repo_parser.add_argument('--type', help='Filter by repository type classification')
    repo_parser.add_argument('--activity', choices=['Active', 'Inactive'], help='Filter by activity status')
    repo_parser.add_argument('--importance', choices=['High', 'Medium', 'Low'], help='Filter by importance level')
    repo_parser.set_defaults(func=github_commands.cmd_repo)
    
    # Google Drive command with subcommands
    google_parser = subparsers.add_parser('google', help='Google Drive commands')
    google_subparsers = google_parser.add_subparsers(dest='subcommand', help='Google Drive subcommands')
    
    # Google Drive list subcommand
    google_list_parser = google_subparsers.add_parser('list', help='List Google Drive files')
    google_list_parser.add_argument('--query', help='Search query for file names')
    google_list_parser.add_argument('--folder', help='Folder ID to list contents of')
    google_list_parser.add_argument('--limit', type=int, default=100, help='Maximum number of files to list')
    
    # Google Drive get document subcommand
    google_get_parser = google_subparsers.add_parser('get', help='Get a Google Drive document')
    google_get_parser.add_argument('doc_id', help='Document ID or URL')
    google_get_parser.add_argument('--format', choices=['md', 'html', 'txt'], default='md', help='Output format (default: md)')
    google_get_parser.add_argument('--output', help='Output file path')
    
    # Google Drive search subcommand
    google_search_parser = google_subparsers.add_parser('search', help='Search within a Google Drive document')
    google_search_parser.add_argument('doc_id', help='Document ID or URL')
    google_search_parser.add_argument('query', help='Search query')
    google_search_parser.add_argument('--output', help='Output file path for search results')
    
    google_parser.set_defaults(func=google_commands.cmd_google)
    
    # AWS command with subcommands
    aws_parser = subparsers.add_parser('aws', help='AWS commands')
    aws_subparsers = aws_parser.add_subparsers(dest='subcommand', help='AWS subcommands')
    
    # AWS run subcommand
    aws_run_parser = aws_subparsers.add_parser('run', help='Run AWS CLI commands with assumed role credentials')
    aws_run_parser.add_argument('--account', '-a', help='Target AWS account ID (optional if default target is set)')
    aws_run_parser.add_argument('--role', '-r', help='Role name to assume')
    aws_run_parser.add_argument('--source-profile', '-s', help='Source profile for role chaining')
    aws_run_parser.add_argument('--saas-account', help='SaaS account ID for role chaining')
    aws_run_parser.add_argument('--saas-role', help='SaaS role name for role chaining')
    aws_run_parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    aws_run_parser.add_argument('aws_args', nargs=argparse.REMAINDER, help='AWS CLI command and arguments')
    
    # AWS config subcommand
    aws_config_parser = aws_subparsers.add_parser('config', help='Configure default settings')
    aws_config_parser.add_argument('--account', '-a', help='Target AWS account ID')
    aws_config_parser.add_argument('--role', '-r', help='Role name to assume')
    aws_config_parser.add_argument('--set-role', help='Set default role')
    aws_config_parser.add_argument('--set-saas-role', help='Set default SaaS role for role chaining')
    aws_config_parser.add_argument('--set-source-profile', help='Set default source profile for role chaining')
    aws_config_parser.add_argument('--source-profile', help='Source profile for role chaining')
    aws_config_parser.add_argument('--saas-account', help='SaaS account ID for role chaining')
    aws_config_parser.add_argument('--saas-role', help='SaaS role name for role chaining')
    aws_config_parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    # AWS recent subcommand
    aws_recent_parser = aws_subparsers.add_parser('recent', help='Show recently used accounts')
    aws_recent_parser.add_argument('--account', '-a', help='Target AWS account ID')
    aws_recent_parser.add_argument('--role', '-r', help='Role name to assume')
    aws_recent_parser.add_argument('--source-profile', '-s', help='Source profile for role chaining')
    aws_recent_parser.add_argument('--saas-account', help='SaaS account ID for role chaining')
    aws_recent_parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    # AWS setup subcommand
    aws_setup_parser = aws_subparsers.add_parser('setup', help='Quick setup for SaaS and target accounts')
    aws_setup_parser.add_argument('--saas-account', '-s', required=True, help='SaaS AWS account ID')
    aws_setup_parser.add_argument('--target-account', '-t', help='Target AWS account ID (optional)')
    aws_setup_parser.add_argument('--role', '-r', help='Role name to assume')
    aws_setup_parser.add_argument('--saas-role', help='SaaS role name for role chaining')
    aws_setup_parser.add_argument('--source-profile', help='Source profile for role chaining')
    aws_setup_parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    # AWS logs subcommand
    aws_logs_parser = aws_subparsers.add_parser('logs', help='Get logs from CloudWatch Logs')
    aws_logs_parser.add_argument('log_group', help='Log group name')
    aws_logs_parser.add_argument('--account', '-a', help='Target AWS account ID (optional if default target is set)')
    aws_logs_parser.add_argument('--role', '-r', help='Role name to assume')
    aws_logs_parser.add_argument('--source-profile', '-s', help='Source profile for role chaining')
    aws_logs_parser.add_argument('--saas-account', help='SaaS account ID for role chaining')
    aws_logs_parser.add_argument('--saas-role', help='SaaS role name for role chaining')
    aws_logs_parser.add_argument('--start-time', help='Start time in ISO format (YYYY-MM-DDTHH:MM:SS)')
    aws_logs_parser.add_argument('--end-time', help='End time in ISO format (YYYY-MM-DDTHH:MM:SS)')
    aws_logs_parser.add_argument('--filter-pattern', help='Filter pattern')
    aws_logs_parser.add_argument('--log-stream', help='Log stream name')
    aws_logs_parser.add_argument('--output', help='Output file path')
    aws_logs_parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    aws_parser.set_defaults(func=aws_commands.cmd_aws)
    
    # Jira command with subcommands
    jira_parser = subparsers.add_parser('jira', help='Jira commands')
    jira_subparsers = jira_parser.add_subparsers(dest='subcommand', help='Jira subcommands')
    
    # Jira get subcommand
    jira_get_parser = jira_subparsers.add_parser('get', help='Get a Jira ticket')
    jira_get_parser.add_argument('ticket_key', help='Jira ticket key (e.g., JIRA-123)')
    jira_get_parser.add_argument('--output', help='Output file path for ticket details')
    
    # Jira search subcommand
    jira_search_parser = jira_subparsers.add_parser('search', help='Search for Jira tickets')
    jira_search_parser.add_argument('--query', help='JQL query to search for tickets')
    jira_search_parser.add_argument('--output', help='Output file path for search results')
    
    # Jira comment subcommand
    jira_comment_parser = jira_subparsers.add_parser('comment', help='Add a comment to a Jira ticket')
    jira_comment_parser.add_argument('ticket_key', help='Jira ticket key (e.g., JIRA-123)')
    jira_comment_parser.add_argument('comment', help='Comment text to add')
    
    jira_parser.set_defaults(func=jira_commands.cmd_jira)
    
    # Notion command with subcommands
    notion_parser = notion_commands.setup_notion_parser(subparsers)
    notion_parser.set_defaults(func=notion_commands.handle_notion_commands)
    
    # Config commands
    config_parser = subparsers.add_parser('config', help='Configuration commands')
    config_subparsers = config_parser.add_subparsers(dest='config_action')
    
    # config show command
    config_show_parser = config_subparsers.add_parser('show', help='Show current configuration')
    
    # config google command
    config_google_parser = config_subparsers.add_parser('google', help='Configure Google Drive')
    config_google_parser.add_argument('--json-file', required=True, help='Path to Google service account JSON file')
    
    # config github command
    config_github_parser = config_subparsers.add_parser('github', help='Configure GitHub')
    config_github_parser.add_argument('--token', required=True, help='GitHub personal access token')
    
    # config jira command
    config_jira_parser = config_subparsers.add_parser('jira', help='Configure Jira')
    config_jira_parser.add_argument('--email', help='Jira email address')
    config_jira_parser.add_argument('--token', help='Jira API token')
    config_jira_parser.add_argument('--server', help='Jira server URL (e.g., https://your-instance.atlassian.net)')
    
    # config notion command
    config_notion_parser = config_subparsers.add_parser('notion', help='Configure Notion')
    config_notion_parser.add_argument('--token', required=True, help='Notion API token')
    
    config_parser.set_defaults(func=config_commands.cmd_config)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'jira' and not args.subcommand:
        jira_parser.print_help()
        sys.exit(1)
    
    if args.command == 'google' and not args.subcommand:
        google_parser.print_help()
        sys.exit(1)
    
    if args.command == 'aws' and not args.subcommand:
        aws_parser.print_help()
        sys.exit(1)
    
    if args.command == 'config' and not args.config_action:
        config_parser.print_help()
        sys.exit(1)
    
    if args.command == 'notion' and not hasattr(args, 'notion_action'):
        notion_parser.print_help()
        sys.exit(1)
    
    args.func(args)

if __name__ == '__main__':
    main()
