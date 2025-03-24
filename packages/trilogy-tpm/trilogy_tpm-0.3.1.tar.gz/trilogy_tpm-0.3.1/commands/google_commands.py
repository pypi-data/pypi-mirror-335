#!/usr/bin/env python3
"""
Google Drive commands for TPM-CLI.
"""

import os
import sys
import json
from tabulate import tabulate
from datetime import datetime
import google_utils

def cmd_google(args):
    """Handle Google Drive commands."""
    if not hasattr(args, 'subcommand') or not args.subcommand:
        print("Error: No subcommand specified for 'google' command")
        print("Available subcommands: list, get, search")
        sys.exit(1)
    
    if args.subcommand == 'list':
        cmd_google_list(args)
    elif args.subcommand == 'get':
        cmd_google_get(args)
    elif args.subcommand == 'search':
        cmd_google_search(args)
    else:
        print(f"Error: Unknown subcommand '{args.subcommand}' for 'google' command")
        sys.exit(1)

def cmd_google_list(args):
    """List Google Drive files matching a query or in a folder."""
    try:
        # Set up cache directory
        google_utils.setup_cache()
        
        # List files
        files = google_utils.list_files(
            query=args.query,
            folder_id=args.folder,
            max_results=args.limit
        )
        
        if not files:
            print("No files found.")
            sys.exit(0)
        
        # Prepare table data
        table_data = []
        for file in files:
            # Format the modified time
            modified_time = file.get('modifiedTime', '')
            if modified_time:
                try:
                    dt = datetime.fromisoformat(modified_time.replace('Z', '+00:00'))
                    modified_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass
            
            # Get location information
            location = "My Drive"
            if 'parent_info' in file and file['parent_info']:
                parent_names = [p.get('name', 'Unknown') for p in file['parent_info']]
                location = " > ".join(parent_names)
            elif 'shared' in file and file['shared']:
                location = "Shared with me"
            
            # Add ownership information
            owner = "Unknown"
            if 'owners' in file and file['owners']:
                owner = file['owners'][0].get('displayName', 'Unknown')
            
            # Add to table data
            table_data.append([
                file.get('name', ''),
                file.get('id', ''),
                file.get('mimeType', '').split('.')[-1],
                modified_time,
                location,
                owner
            ])
        
        # Sort by modified time (newest first)
        table_data.sort(key=lambda x: x[3], reverse=True)
        
        # Output table
        headers = ["Name", "ID", "Type", "Modified", "Location", "Owner"]
        table = tabulate(table_data, headers=headers, tablefmt="grid")
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write("# Google Drive Files\n\n")
                f.write("| " + " | ".join(headers) + " |\n")
                f.write("| " + " | ".join(["---"] * len(headers)) + " |\n")
                
                for row in table_data:
                    f.write("| " + " | ".join(str(cell) for cell in row) + " |\n")
            
            print(f"Results saved to {args.output}")
        else:
            print(f"\nFound {len(files)} files:")
            print(table)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def cmd_google_get(args):
    """Get a Google Drive document and save it in the specified format."""
    try:
        # Set up cache directory
        google_utils.setup_cache()
        
        # Extract document ID from URL or ID
        doc_id = google_utils.extract_doc_id(args.doc_id)
        
        # Get document content
        content = google_utils.get_document(doc_id, args.format)
        
        if not content:
            print("Failed to retrieve document content.")
            sys.exit(1)
        
        # Output content
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Document saved to {args.output}")
        else:
            print(content)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def cmd_google_search(args):
    """Search for text within a Google Drive document."""
    try:
        # Set up cache directory
        google_utils.setup_cache()
        
        # Extract document ID from URL or ID
        doc_id = google_utils.extract_doc_id(args.doc_id)
        
        # Search document
        results = google_utils.search_document_content(doc_id, args.query)
        
        if not results:
            print(f"No matches found for '{args.query}' in the document.")
            sys.exit(0)
        
        # Format results
        formatted_results = f"# Search Results for '{args.query}'\n\n"
        
        for i, result in enumerate(results, 1):
            formatted_results += f"## Match {i}\n\n"
            formatted_results += f"```\n{result['context']}\n```\n\n"
        
        # Output results
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(formatted_results)
            print(f"Search results saved to {args.output}")
        else:
            print(formatted_results)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
