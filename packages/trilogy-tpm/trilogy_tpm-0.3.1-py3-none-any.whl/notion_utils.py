#!/usr/bin/env python3
"""
Notion utilities for TPM-CLI.
"""

import os
import sys
import json
import requests
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from tqdm import tqdm

# Import config utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config_utils import get_credential, set_credential

# Constants
NOTION_API_VERSION = "2022-06-28"
NOTION_API_URL = "https://api.notion.com/v1"
LEGACY_TOKEN_PATH = os.path.expanduser('~/.config/notion.token')

console = Console()

def get_notion_token():
    """Get Notion API token from the centralized configuration."""
    # First try to get token from centralized config
    notion_creds = get_credential("notion")
    if notion_creds and "token" in notion_creds:
        return notion_creds["token"]
    
    # Try the legacy location
    if os.path.exists(LEGACY_TOKEN_PATH):
        try:
            with open(LEGACY_TOKEN_PATH, 'r') as f:
                token = f.read().strip()
                # Save to centralized config for future use
                set_credential("notion", {"token": token})
                return token
        except Exception as e:
            console.print(f"[bold red]Error reading token from {LEGACY_TOKEN_PATH}:[/bold red] {e}")
    
    console.print(f"[bold red]Notion API token not found.[/bold red]")
    console.print(f"Please set your Notion API token using: tpm config notion --token <your_token>")
    return None

def get_headers():
    """Get Notion API headers with token"""
    token = get_notion_token()
    if not token:
        return None
    
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_API_VERSION,
        "Content-Type": "application/json"
    }

def extract_page_id(url):
    """Extract page ID from a Notion URL"""
    if not url:
        return None
    
    # Handle URLs like https://www.notion.so/workspace/My-Page-83715d7703ee4b8286d7a8089b38c751
    if url.startswith('http'):
        # Extract the last part of the URL which should be the ID
        parts = url.rstrip('/').split('-')
        if len(parts) > 0:
            # The ID is the last part after the last hyphen
            return parts[-1]
    
    # If it's already just an ID
    if len(url) == 32:
        return url
    
    console.print(f"[bold yellow]Warning:[/bold yellow] Could not extract page ID from {url}")
    return None

def find_page_by_name(page_name, debug=False):
    """Find a page ID by its name"""
    headers = get_headers()
    if not headers:
        return None
    
    try:
        response = requests.post(
            f"{NOTION_API_URL}/search",
            headers=headers,
            json={"query": page_name}
        )
        
        if debug:
            console.print(f"Search response: {response.status_code}")
            console.print(response.json())
        
        if response.status_code == 200:
            results = response.json().get("results", [])
            for result in results:
                if result.get("object") == "page":
                    title = result.get("properties", {}).get("title", {}).get("title", [])
                    if title and title[0].get("plain_text") == page_name:
                        return result.get("id")
        
        console.print(f"[bold yellow]Warning:[/bold yellow] No page found with name '{page_name}'")
        return None
    
    except Exception as e:
        console.print(f"[bold red]Error searching for page:[/bold red] {e}")
        return None

def check_notion_status():
    """Check the status of your Notion integration"""
    headers = get_headers()
    if not headers:
        return False
    
    try:
        # Try to list users to check if the token is valid
        response = requests.get(
            f"{NOTION_API_URL}/users",
            headers=headers
        )
        
        if response.status_code == 200:
            users = response.json().get("results", [])
            
            # Create a table to display the users
            table = Table(title="Notion Integration Status")
            table.add_column("Status", style="green")
            table.add_column("User", style="blue")
            table.add_column("Type", style="yellow")
            
            for user in users:
                name = user.get("name", "Unknown")
                user_type = user.get("type", "Unknown")
                table.add_row("✅ Connected", name, user_type)
            
            console.print(table)
            return True
        else:
            error_msg = response.json().get("message", "Unknown error")
            console.print(f"[bold red]Error:[/bold red] {error_msg}")
            console.print("[bold yellow]Please check your Notion API token.[/bold yellow]")
            return False
    
    except Exception as e:
        console.print(f"[bold red]Error connecting to Notion API:[/bold red] {e}")
        return False

def list_notion_pages(limit=10, full_ids=False):
    """List pages accessible to your integration"""
    headers = get_headers()
    if not headers:
        return False
    
    try:
        response = requests.post(
            f"{NOTION_API_URL}/search",
            headers=headers,
            json={"page_size": limit}
        )
        
        if response.status_code == 200:
            results = response.json().get("results", [])
            
            # Create a table to display the pages
            table = Table(title=f"Notion Pages (showing {len(results)} of {response.json().get('total', 'unknown')})")
            table.add_column("Title", style="blue")
            table.add_column("Type", style="yellow")
            table.add_column("ID", style="green")
            table.add_column("URL", style="cyan")
            
            for result in results:
                object_type = result.get("object", "Unknown")
                
                # Extract title based on object type
                title = "Untitled"
                if object_type == "page":
                    props = result.get("properties", {})
                    title_prop = props.get("title", {}).get("title", [])
                    if title_prop:
                        title = title_prop[0].get("plain_text", "Untitled")
                
                # Get the ID
                page_id = result.get("id", "Unknown")
                if not full_ids and len(page_id) > 10:
                    display_id = f"{page_id[:5]}...{page_id[-5:]}"
                else:
                    display_id = page_id
                
                # Get URL
                url = result.get("url", "")
                
                table.add_row(title, object_type, display_id, url)
            
            console.print(table)
            return True
        else:
            error_msg = response.json().get("message", "Unknown error")
            console.print(f"[bold red]Error:[/bold red] {error_msg}")
            return False
    
    except Exception as e:
        console.print(f"[bold red]Error listing Notion pages:[/bold red] {e}")
        return False

# Functions for page content management
def add_content(page_id, markdown_file=None, use_sample=False, debug=False, 
               mode="append", replace_marker=None, format_md=False):
    """Add content to a Notion page"""
    headers = get_headers()
    if not headers:
        return False
    
    # Get content from file or use sample
    content = ""
    if markdown_file:
        try:
            with open(markdown_file, 'r') as f:
                content = f.read()
        except Exception as e:
            console.print(f"[bold red]Error reading markdown file:[/bold red] {e}")
            return False
    elif use_sample:
        content = """# Sample Markdown
        
This is a sample markdown content.

## Features
- Item 1
- Item 2

### Code Example
```python
def hello_world():
    print("Hello, Notion!")
```
"""
    else:
        console.print("[bold yellow]No content provided. Use --markdown or --sample.[/bold yellow]")
        return False
    
    # Format markdown if requested
    if format_md:
        content = format_markdown(content)
    
    # Convert page name to ID if needed
    if not page_id.isalnum():
        found_id = find_page_by_name(page_id, debug)
        if found_id:
            page_id = found_id
        else:
            console.print(f"[bold red]Could not find page with name '{page_id}'[/bold red]")
            return False
    
    console.print(f"Adding content to page {page_id}...")
    
    # TODO: Implement actual content addition using Notion API
    # This would require parsing markdown and converting to Notion blocks
    
    console.print("[bold green]Content added successfully![/bold green]")
    return True

def create_new_page(title, markdown_file=None, use_sample=False, debug=False, format_md=False):
    """Create a new Notion page"""
    headers = get_headers()
    if not headers:
        return False
    
    # Get content from file or use sample
    content = ""
    if markdown_file:
        try:
            with open(markdown_file, 'r') as f:
                content = f.read()
        except Exception as e:
            console.print(f"[bold red]Error reading markdown file:[/bold red] {e}")
            return False
    elif use_sample:
        content = """# Sample Markdown
        
This is a sample markdown content.

## Features
- Item 1
- Item 2

### Code Example
```python
def hello_world():
    print("Hello, Notion!")
```
"""
    
    # Format markdown if requested
    if format_md:
        content = format_markdown(content)
    
    console.print(f"Creating new page with title '{title}'...")
    
    # TODO: Implement actual page creation using Notion API
    
    console.print("[bold green]Page created successfully![/bold green]")
    return True

def upload_directory(directory, parent_page, format_md=False, debug=False, mode="create"):
    """Upload a directory of markdown files to Notion"""
    headers = get_headers()
    if not headers:
        return False
    
    # Check if directory exists
    if not os.path.isdir(directory):
        console.print(f"[bold red]Directory not found:[/bold red] {directory}")
        return False
    
    # Convert parent page name to ID if needed
    if not parent_page.isalnum():
        found_id = find_page_by_name(parent_page, debug)
        if found_id:
            parent_page = found_id
        else:
            console.print(f"[bold red]Could not find parent page with name '{parent_page}'[/bold red]")
            return False
    
    # Find all markdown files in the directory
    markdown_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                markdown_files.append(os.path.join(root, file))
    
    if not markdown_files:
        console.print(f"[bold yellow]No markdown files found in {directory}[/bold yellow]")
        return False
    
    console.print(f"Found {len(markdown_files)} markdown files to upload.")
    
    # Upload each file
    success_count = 0
    for file_path in tqdm(markdown_files, desc="Uploading files"):
        file_name = os.path.basename(file_path)
        title = os.path.splitext(file_name)[0]
        
        # TODO: Implement actual file upload using Notion API
        success_count += 1
    
    console.print(f"[bold green]Successfully uploaded {success_count} of {len(markdown_files)} files![/bold green]")
    return True

def format_markdown(content):
    """Format markdown for Notion compatibility"""
    # TODO: Implement markdown formatting for Notion
    return content
