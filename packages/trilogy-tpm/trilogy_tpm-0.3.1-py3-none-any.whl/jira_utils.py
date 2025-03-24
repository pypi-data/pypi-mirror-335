#!/usr/bin/env python3
"""
Jira utilities for TPM-CLI.
"""

import os
import sys
import json
import logging
import requests
import base64
from tabulate import tabulate
import markdown
from jira import JIRA
from datetime import datetime

# Import config utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config_utils import get_credential, set_credential

# Set up logging
logger = logging.getLogger('tpm.jira')
handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Constants
DEFAULT_JIRA_SERVER = "https://trilogy-eng.atlassian.net"

# Legacy paths for backward compatibility
CONFIG_DIR = os.path.expanduser("~/.config/jira")
EMAIL_PATH = os.path.join(CONFIG_DIR, "email")
TOKEN_PATH = os.path.join(CONFIG_DIR, "token")

def get_jira_credentials():
    """Get Jira credentials from config."""
    # Try to get credentials from centralized config
    email = get_credential("jira", "email")
    token = get_credential("jira", "token")
    
    # If not found, try legacy paths
    if not email and os.path.exists(EMAIL_PATH):
        try:
            with open(EMAIL_PATH, 'r') as f:
                email = f.read().strip()
        except Exception as e:
            logger.error(f"Error reading Jira email: {e}")
    
    if not token and os.path.exists(TOKEN_PATH):
        try:
            with open(TOKEN_PATH, 'r') as f:
                token = f.read().strip()
        except Exception as e:
            logger.error(f"Error reading Jira token: {e}")
    
    if not email or not token:
        raise ValueError("Jira credentials not found. Please run 'tpm config jira --email <email> --token <token>' to set up your credentials.")
    
    return email, token

def get_jira_client():
    """Create and return a JIRA client."""
    email, token = get_jira_credentials()
    jira_server = get_credential("jira", "server") or DEFAULT_JIRA_SERVER
    
    # Enable debug logging for JIRA client
    logging.getLogger('jira').setLevel(logging.DEBUG)
    
    # Create the JIRA client with proper authentication
    return JIRA(
        server=jira_server,
        basic_auth=(email, token),
        options={
            'verify': True,
            'headers': {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        }
    )

def get_ticket(ticket_key, output_format='table', output_file=None):
    """Fetch a Jira ticket by its key."""
    jira = get_jira_client()
    
    try:
        issue = jira.issue(ticket_key)
        
        ticket = {
            'key': issue.key,
            'summary': issue.fields.summary,
            'status': issue.fields.status.name,
            'resolution': issue.fields.resolution.name if hasattr(issue.fields, 'resolution') and issue.fields.resolution else 'Unresolved',
            'created': issue.fields.created,
            'updated': issue.fields.updated,
            'assignee': str(issue.fields.assignee) if issue.fields.assignee else 'Unassigned',
            'reporter': str(issue.fields.reporter) if issue.fields.reporter else 'Unknown',
            'description': issue.fields.description if issue.fields.description else 'No description'
        }
        
        # Add comments
        if hasattr(issue.fields, 'comment') and issue.fields.comment:
            comments = []
            for comment in issue.fields.comment.comments:
                comments.append({
                    'author': str(comment.author),
                    'created': comment.created,
                    'body': comment.body
                })
            ticket['comments'] = comments
        
        if output_format == 'json':
            output_content = json.dumps(ticket, indent=2, default=str)
        elif output_format == 'markdown':
            output_content = f"# [{ticket['key']}](https://trilogy-eng.atlassian.net/browse/{ticket['key']}) - {ticket['summary']}\n\n"
            output_content += f"**Status**: {ticket['status']}  \n"
            output_content += f"**Resolution**: {ticket['resolution']}  \n"
            output_content += f"**Created**: {ticket['created']}  \n"
            output_content += f"**Updated**: {ticket['updated']}  \n"
            output_content += f"**Assignee**: {ticket['assignee']}  \n"
            output_content += f"**Reporter**: {ticket['reporter']}  \n\n"
            
            output_content += "## Description\n\n```\n"
            output_content += ticket['description']
            output_content += "\n```\n\n"
            
            if 'comments' in ticket:
                output_content += "## Comments\n\n"
                for comment in ticket['comments']:
                    output_content += f"### {comment['author']} - {comment['created']}\n\n"
                    output_content += f"```\n{comment['body']}\n```\n\n"
        else:  # table format
            # Print ticket details
            table_data = []
            for key, value in ticket.items():
                if key != 'comments' and key != 'description':
                    table_data.append([key, str(value)])
            
            output_content = "Ticket Details:\n"
            output_content += tabulate(table_data, headers=["Field", "Value"], tablefmt="grid")
            output_content += "\n\nDescription:\n"
            output_content += ticket['description'][:500] + "..." if len(ticket['description']) > 500 else ticket['description']
            
            if 'comments' in ticket:
                output_content += "\n\nComments:\n"
                comment_data = []
                for comment in ticket['comments']:
                    body_preview = comment['body'][:100] + "..." if len(comment['body']) > 100 else comment['body']
                    comment_data.append([comment['author'], comment['created'], body_preview])
                
                output_content += tabulate(comment_data, headers=["Author", "Created", "Comment"], tablefmt="grid")
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(output_content)
            print(f"Output written to {output_file}")
        else:
            print(output_content)
            
        return ticket
    except Exception as e:
        print(f"Error fetching {ticket_key}: {e}")
        sys.exit(1)

def get_ticket_direct(ticket_key, output_format='md', output_file=None):
    """Get a Jira ticket by its key using direct HTTP requests."""
    try:
        # Get credentials
        email, token = get_jira_credentials()
        jira_server = get_credential("jira", "server") or DEFAULT_JIRA_SERVER
        
        # Create auth string
        auth_str = f"{email}:{token}"
        auth_bytes = auth_str.encode('ascii')
        base64_bytes = base64.b64encode(auth_bytes)
        base64_auth = base64_bytes.decode('ascii')
        
        # Set up headers
        headers = {
            'Authorization': f'Basic {base64_auth}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Make a request to the issue endpoint
        url = f"{jira_server}/rest/api/2/issue/{ticket_key}"
        logger.info(f"Making direct request to: {url}")
        
        response = requests.get(url, headers=headers, verify=True)
        
        # Check response
        if response.status_code == 200:
            ticket_data = response.json()
            
            # Format the output
            if output_format.lower() in ['md', 'markdown']:
                output = format_ticket_as_markdown(ticket_data)
            else:  # Default to JSON
                output = json.dumps(ticket_data, indent=2)
            
            # Write to file or print to console
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(output)
                print(f"Ticket information saved to {output_file}")
            else:
                print(output)
                
            return ticket_data
        else:
            error_msg = f"Error fetching {ticket_key}: HTTP {response.status_code}"
            if response.text:
                error_msg += f"\nResponse: {response.text}"
            logger.error(error_msg)
            print(error_msg)
            raise Exception(error_msg)
    
    except Exception as e:
        logger.error(f"Error fetching {ticket_key}: {str(e)}")
        print(f"Error fetching {ticket_key}: {str(e)}")
        # Re-raise the exception to be caught by the caller
        raise

def search_tickets(query=None, limit=10, output_format='table', output_file=None):
    """Search for Jira tickets using JQL."""
    if not query:
        query = "project = CONTENTLY ORDER BY created DESC"
    
    jira = get_jira_client()
    
    try:
        issues = jira.search_issues(query, maxResults=limit)
        
        results = []
        for issue in issues:
            results.append({
                'key': issue.key,
                'summary': issue.fields.summary,
                'status': issue.fields.status.name,
                'assignee': str(issue.fields.assignee) if issue.fields.assignee else 'Unassigned',
                'created': issue.fields.created,
                'updated': issue.fields.updated
            })
        
        if output_format == 'json':
            output_content = json.dumps(results, indent=2, default=str)
        elif output_format == 'markdown':
            output_content = f"# Jira Search Results\n\n"
            output_content += f"Query: `{query}`  \n"
            output_content += f"Found {len(results)} results  \n\n"
            
            output_content += "| Key | Summary | Status | Assignee | Updated |\n"
            output_content += "|-----|---------|--------|----------|--------|\n"
            
            for result in results:
                output_content += f"| [{result['key']}](https://trilogy-eng.atlassian.net/browse/{result['key']}) "
                output_content += f"| {result['summary']} "
                output_content += f"| {result['status']} "
                output_content += f"| {result['assignee']} "
                output_content += f"| {result['updated']} |\n"
        else:  # table format
            table_data = []
            for result in results:
                table_data.append([
                    result['key'], 
                    result['summary'][:50] + "..." if len(result['summary']) > 50 else result['summary'],
                    result['status'],
                    result['assignee'],
                    result['updated']
                ])
            
            output_content = f"Query: {query}\n"
            output_content += f"Found {len(results)} results\n\n"
            output_content += tabulate(table_data, headers=["Key", "Summary", "Status", "Assignee", "Updated"], tablefmt="grid")
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(output_content)
            print(f"Output written to {output_file}")
        else:
            print(output_content)
            
        return results
    except Exception as e:
        print(f"Error searching tickets: {e}")
        sys.exit(1)

def add_comment(ticket_key, comment_text):
    """Add a comment to a Jira ticket."""
    jira = get_jira_client()
    
    try:
        issue = jira.issue(ticket_key)
        jira.add_comment(issue, comment_text)
        print(f"Comment added to {ticket_key}")
    except Exception as e:
        print(f"Error adding comment to {ticket_key}: {e}")
        sys.exit(1)

def set_config(email=None, token=None, server=None):
    """Set Jira configuration."""
    # Get current credentials
    current_email, current_token = None, None
    try:
        current_email, current_token = get_jira_credentials()
    except:
        pass
    
    # Update with new values if provided
    if email:
        set_credential("jira", email, "email")
    elif current_email:
        set_credential("jira", current_email, "email")
    
    if token:
        set_credential("jira", token, "token")
    elif current_token:
        set_credential("jira", current_token, "token")
    
    if server:
        set_credential("jira", server, "server")
    
    print("Jira configuration updated successfully.")

def show_config():
    """Show Jira configuration."""
    try:
        email, token = get_jira_credentials()
        server = get_credential("jira", "server")
        if server is None:
            server = DEFAULT_JIRA_SERVER
        print("Jira Configuration:")
        print(f"Server: {server}")
        print(f"Email: {email}")
        print(f"Token: {'*' * 8}{token[-4:] if len(token) > 4 else ''}")
        print(f"Config directory: {os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}")
    except Exception as e:
        print(f"Error: {e}")

def format_ticket_as_markdown(ticket_data):
    output = f"# [{ticket_data['key']}]({DEFAULT_JIRA_SERVER}/browse/{ticket_data['key']}) - {ticket_data['fields']['summary']}\n\n"
    output += f"**Status**: {ticket_data['fields']['status']['name']}  \n"
    if 'resolution' in ticket_data['fields'] and ticket_data['fields']['resolution']:
        output += f"**Resolution**: {ticket_data['fields']['resolution']['name']}  \n"
    else:
        output += f"**Resolution**: Unresolved  \n"
    output += f"**Created**: {ticket_data['fields']['created']}  \n"
    output += f"**Updated**: {ticket_data['fields']['updated']}  \n"
    
    # Handle assignee safely
    if 'assignee' in ticket_data['fields'] and ticket_data['fields']['assignee']:
        assignee = ticket_data['fields']['assignee']
        assignee_name = assignee.get('displayName') or assignee.get('name') or "Unknown"
        output += f"**Assignee**: {assignee_name}  \n"
    else:
        output += f"**Assignee**: Unassigned  \n"
    
    # Handle reporter safely
    if 'reporter' in ticket_data['fields'] and ticket_data['fields']['reporter']:
        reporter = ticket_data['fields']['reporter']
        reporter_name = reporter.get('displayName') or reporter.get('name') or "Unknown"
        output += f"**Reporter**: {reporter_name}  \n\n"
    else:
        output += f"**Reporter**: Unknown  \n\n"
    
    if 'description' in ticket_data['fields'] and ticket_data['fields']['description']:
        output += "## Description\n\n```\n"
        output += ticket_data['fields']['description']
        output += "\n```\n\n"
    
    if 'comment' in ticket_data['fields'] and ticket_data['fields']['comment']:
        output += "## Comments\n\n"
        for comment in ticket_data['fields']['comment']['comments']:
            author = comment['author']
            author_name = author.get('displayName') or author.get('name') or "Unknown"
            output += f"### {author_name} - {comment['created']}\n\n"
            output += f"```\n{comment['body']}\n```\n\n"
    
    return output

def test_jira_connection():
    """Test the Jira connection with a simple API request."""
    try:
        # Get credentials
        email, token = get_jira_credentials()
        jira_server = get_credential("jira", "server") or DEFAULT_JIRA_SERVER
        
        # Create auth string
        auth_str = f"{email}:{token}"
        auth_bytes = auth_str.encode('ascii')
        base64_bytes = base64.b64encode(auth_bytes)
        base64_auth = base64_bytes.decode('ascii')
        
        # Set up headers
        headers = {
            'Authorization': f'Basic {base64_auth}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Make a request to the server info endpoint
        url = f"{jira_server}/rest/api/2/serverInfo"
        logger.info(f"Testing connection to: {url}")
        
        response = requests.get(url, headers=headers, verify=True)
        
        # Check response
        if response.status_code == 200:
            server_info = response.json()
            print(f"Successfully connected to Jira server: {server_info.get('baseUrl', jira_server)}")
            print(f"Server version: {server_info.get('version', 'Unknown')}")
            print(f"Server title: {server_info.get('serverTitle', 'Unknown')}")
            return True
        else:
            logger.error(f"Error connecting to Jira: {response.status_code}")
            logger.error(f"Response: {response.text}")
            print(f"Error connecting to Jira server: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"Error testing Jira connection: {str(e)}")
        print(f"Error testing Jira connection: {str(e)}")
        return False

def list_jira_projects():
    """List all accessible Jira projects."""
    try:
        # Get credentials
        email, token = get_jira_credentials()
        jira_server = get_credential("jira", "server") or DEFAULT_JIRA_SERVER
        
        # Create auth string
        auth_str = f"{email}:{token}"
        auth_bytes = auth_str.encode('ascii')
        base64_bytes = base64.b64encode(auth_bytes)
        base64_auth = base64_bytes.decode('ascii')
        
        # Set up headers
        headers = {
            'Authorization': f'Basic {base64_auth}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Make a request to the projects endpoint
        url = f"{jira_server}/rest/api/2/project"
        logger.info(f"Fetching projects from: {url}")
        
        response = requests.get(url, headers=headers, verify=True)
        
        # Check response
        if response.status_code == 200:
            projects = response.json()
            print(f"Found {len(projects)} accessible projects:")
            
            # Print table header
            print("\n{:<10} {:<30} {:<40}".format("Key", "Name", "URL"))
            print("-" * 80)
            
            # Print each project
            for project in projects:
                print("{:<10} {:<30} {:<40}".format(
                    project.get('key', 'N/A'),
                    project.get('name', 'N/A')[:30],
                    f"{jira_server}/projects/{project.get('key', 'N/A')}"
                ))
            
            return projects
        else:
            logger.error(f"Error fetching projects: {response.status_code}")
            logger.error(f"Response: {response.text}")
            print(f"Error fetching projects: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return []
    
    except Exception as e:
        logger.error(f"Error listing Jira projects: {str(e)}")
        print(f"Error listing Jira projects: {str(e)}")
        return []
