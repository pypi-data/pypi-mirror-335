#!/usr/bin/env python3
"""
Google Drive utilities for TPM-CLI.
"""

import os
import json
import boto3
import html2text
import re
import sys
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Import config utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config_utils import get_credential, set_credential

# Constants
SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents'
]
CACHE_DIR = os.path.expanduser("~/.tpm-cli/google_cache")
CREDENTIALS_DIR = os.path.expanduser("~/.tpm-cli")
LOCAL_CREDENTIALS_FILE = os.path.expanduser("~/.tpm-cli/credentials.json")
LEGACY_CREDENTIALS_FILE = os.path.expanduser("~/.config/google/creds.json")

# Add a mock mode flag for testing
MOCK_MODE = os.environ.get('TPM_MOCK_GOOGLE', '').lower() in ('true', '1', 'yes')

def setup_cache():
    """Set up the cache directory if it doesn't exist."""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR, exist_ok=True)
    
    if not os.path.exists(CREDENTIALS_DIR):
        os.makedirs(CREDENTIALS_DIR, exist_ok=True)

def get_credentials():
    """Load Google API credentials from local file or AWS Secrets Manager."""
    # Check if we're in mock mode for testing
    if MOCK_MODE:
        print("Using mock credentials for testing")
        # Return a mock credentials object that won't actually be used for API calls
        class MockCredentials:
            def __init__(self):
                pass
        return MockCredentials()
    
    # First try to get credentials from centralized config
    google_creds = get_credential("google")
    if google_creds:
        try:
            return service_account.Credentials.from_service_account_info(
                google_creds, scopes=SCOPES
            )
        except Exception as e:
            print(f"Error loading Google credentials from centralized config: {e}")
    
    # Then try the standard credentials file location
    if os.path.exists(LOCAL_CREDENTIALS_FILE):
        try:
            with open(LOCAL_CREDENTIALS_FILE, 'r') as f:
                creds_data = json.load(f)
                # Save to centralized config for future use
                set_credential("google", creds_data)
                return service_account.Credentials.from_service_account_info(
                    creds_data, scopes=SCOPES
                )
        except Exception as e:
            print(f"Error loading Google credentials from {LOCAL_CREDENTIALS_FILE}: {e}")
    
    # Try the legacy location
    if os.path.exists(LEGACY_CREDENTIALS_FILE):
        try:
            with open(LEGACY_CREDENTIALS_FILE, 'r') as f:
                creds_data = json.load(f)
                # Save to centralized config for future use
                set_credential("google", creds_data)
                return service_account.Credentials.from_service_account_info(
                    creds_data, scopes=SCOPES
                )
        except Exception as e:
            print(f"Error loading Google credentials from {LEGACY_CREDENTIALS_FILE}: {e}")
    
    # Finally, try AWS Secrets Manager
    try:
        # Get the AWS region from environment variable or default to us-east-1
        region = os.environ.get('AWS_REGION', 'us-east-1')
        
        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region
        )
        
        # Get the secret value
        secret_name = os.environ.get('GOOGLE_CREDENTIALS_SECRET', 'google-drive-service-account')
        response = client.get_secret_value(SecretId=secret_name)
        
        # Parse the secret value as JSON
        secret = json.loads(response['SecretString'])
        
        # Save the credentials to the local file for future use
        with open(LOCAL_CREDENTIALS_FILE, 'w') as f:
            json.dump(secret, f)
        
        # Save to centralized config for future use
        set_credential("google", secret)
        
        # Create credentials from the secret
        return service_account.Credentials.from_service_account_info(
            secret, scopes=SCOPES
        )
    except Exception as e:
        print(f"Error loading Google credentials from AWS Secrets Manager: {e}")
        print("Please make sure you have valid Google Drive API credentials.")
        print(f"You can place them in {LOCAL_CREDENTIALS_FILE} or set up AWS Secrets Manager.")
        return None

def extract_doc_id(doc_url_or_id):
    """Extract the document ID from a Google Doc URL or ID."""
    # If it's already just an ID (no slashes or dots)
    if re.match(r'^[a-zA-Z0-9_-]+$', doc_url_or_id):
        return doc_url_or_id
    
    # Extract from URL patterns
    patterns = [
        r'https://docs.google.com/document/d/([a-zA-Z0-9_-]+)',  # Standard doc URL
        r'https://drive.google.com/file/d/([a-zA-Z0-9_-]+)',     # Drive file URL
        r'https://drive.google.com/open\?id=([a-zA-Z0-9_-]+)'    # Open URL
    ]
    
    for pattern in patterns:
        match = re.search(pattern, doc_url_or_id)
        if match:
            return match.group(1)
    
    # If no patterns match, return the original string
    return doc_url_or_id

def list_files(query=None, folder_id=None, max_results=100):
    """List files in Google Drive matching the query or in a specific folder."""
    if MOCK_MODE:
        # Return mock data for testing
        return [
            {
                'name': 'Test Document 1',
                'id': 'abc123',
                'mimeType': 'application/vnd.google-apps.document',
                'modifiedTime': '2025-03-22T19:30:00Z',
                'parents': ['root']
            },
            {
                'name': 'Test Spreadsheet',
                'id': '1hMxNtMh1_fB-tv0A6p4Wqza9hPp8sXcwMJNeQcbc54k',
                'mimeType': 'application/vnd.google-apps.spreadsheet',
                'modifiedTime': '2025-03-21T15:45:00Z',
                'parents': ['root']
            },
            {
                'name': 'Test Presentation',
                'id': 'def456',
                'mimeType': 'application/vnd.google-apps.presentation',
                'modifiedTime': '2025-03-20T10:15:00Z',
                'parents': ['root']
            },
            {
                'name': 'Project Plan',
                'id': 'ghi789',
                'mimeType': 'application/vnd.google-apps.document',
                'modifiedTime': '2025-03-19T08:30:00Z',
                'parents': ['root']
            },
            {
                'name': 'Budget',
                'id': 'jkl012',
                'mimeType': 'application/vnd.google-apps.spreadsheet',
                'modifiedTime': '2025-03-18T14:20:00Z',
                'parents': ['root']
            }
        ][:max_results]
    
    # Get credentials and build the Drive API client
    credentials = get_credentials()
    service = build('drive', 'v3', credentials=credentials)
    
    # Prepare the query
    drive_query = []
    if query:
        drive_query.append(f"name contains '{query}'")
    if folder_id:
        drive_query.append(f"'{folder_id}' in parents")
    
    # Execute the list request
    try:
        results = service.files().list(
            q=" and ".join(drive_query) if drive_query else None,
            pageSize=max_results,
            fields="files(id, name, mimeType, modifiedTime, parents, shared, sharedWithMeTime, owners)",
            includeItemsFromAllDrives=True,
            supportsAllDrives=True
        ).execute()
        
        files = results.get('files', [])
        
        # For each file, get additional information about its location
        for file in files:
            # Get parent folder names if available
            if 'parents' in file and file['parents']:
                try:
                    parent_info = []
                    for parent_id in file['parents']:
                        parent = service.files().get(
                            fileId=parent_id,
                            fields="name,id",
                            supportsAllDrives=True
                        ).execute()
                        parent_info.append({
                            'id': parent_id,
                            'name': parent.get('name', 'Unknown')
                        })
                    file['parent_info'] = parent_info
                except Exception as e:
                    file['parent_info'] = [{'id': p, 'name': 'Error fetching name'} for p in file['parents']]
        
        return files
    except Exception as e:
        print(f"Error listing files: {str(e)}")
        return []

def get_document_type(doc_id, credentials=None):
    """Determine the type of Google Drive document."""
    if MOCK_MODE:
        # For testing, use hardcoded IDs
        if doc_id == '1hMxNtMh1_fB-tv0A6p4Wqza9hPp8sXcwMJNeQcbc54k':
            return 'spreadsheet'
        elif doc_id in ['abc123', 'ghi789']:
            return 'document'
        elif doc_id == 'def456':
            return 'presentation'
        else:
            return 'unknown'
    
    if credentials is None:
        credentials = get_credentials()
    
    service = build('drive', 'v3', credentials=credentials)
    
    try:
        file = service.files().get(
            fileId=doc_id,
            fields='mimeType',
            supportsAllDrives=True
        ).execute()
        
        mime_type = file.get('mimeType', '')
        
        if 'spreadsheet' in mime_type:
            return 'spreadsheet'
        elif 'document' in mime_type:
            return 'document'
        elif 'presentation' in mime_type:
            return 'presentation'
        else:
            return 'generic'
    except Exception as e:
        print(f"Error determining document type: {str(e)}")
        return 'unknown'

def get_docs_document(doc_id, format='md', credentials=None):
    """Get a Google Docs document in the specified format."""
    if MOCK_MODE:
        if format == 'md':
            return f"# Mock Google Doc\n\nThis is a mock Google Doc for {doc_id}.\n\n## Section 1\n\nSome content here.\n\n## Section 2\n\nMore content here."
        elif format == 'html':
            return f"<html><body><h1>Mock Google Doc</h1><p>This is a mock Google Doc for {doc_id}.</p></body></html>"
        else:  # txt
            return f"Mock Google Doc\n\nThis is a mock Google Doc for {doc_id}.\n\nSection 1\n\nSome content here.\n\nSection 2\n\nMore content here."
    
    if credentials is None:
        credentials = get_credentials()
    
    service = build('docs', 'v1', credentials=credentials)
    
    try:
        # Get document content
        doc = service.documents().get(documentId=doc_id).execute()
        
        # Process the document content based on format
        if format == 'md':
            return convert_doc_to_markdown(doc)
        elif format == 'html':
            return convert_doc_to_html(doc)
        else:  # txt
            return convert_doc_to_text(doc)
    except Exception as e:
        print(f"Error retrieving Google Doc: {str(e)}")
        return None

def get_sheets_document(doc_id, format='md', credentials=None):
    """Get a Google Sheets document in the specified format."""
    if MOCK_MODE:
        if format == 'md':
            return """# Test Spreadsheet

| Column A | Column B | Column C |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |
| Value 4  | Value 5  | Value 6  |
| Value 7  | Value 8  | Value 9  |

This is a mock spreadsheet for testing purposes.
"""
        elif format == 'html':
            return """<html>
<head><title>Test Spreadsheet</title></head>
<body>
<h1>Test Spreadsheet</h1>
<table>
<tr><th>Column A</th><th>Column B</th><th>Column C</th></tr>
<tr><td>Value 1</td><td>Value 2</td><td>Value 3</td></tr>
<tr><td>Value 4</td><td>Value 5</td><td>Value 6</td></tr>
<tr><td>Value 7</td><td>Value 8</td><td>Value 9</td></tr>
</table>
<p>This is a mock spreadsheet for testing purposes.</p>
</body>
</html>"""
        else:  # txt
            return """Test Spreadsheet

Column A | Column B | Column C
Value 1  | Value 2  | Value 3
Value 4  | Value 5  | Value 6
Value 7  | Value 8  | Value 9

This is a mock spreadsheet for testing purposes.
"""
    
    if credentials is None:
        credentials = get_credentials()
    
    service = build('sheets', 'v4', credentials=credentials)
    
    try:
        # Get spreadsheet metadata
        spreadsheet = service.spreadsheets().get(spreadsheetId=doc_id).execute()
        title = spreadsheet.get('properties', {}).get('title', 'Spreadsheet')
        
        # Get all sheet data
        result = service.spreadsheets().values().batchGet(
            spreadsheetId=doc_id,
            ranges=get_sheet_ranges(spreadsheet),
            valueRenderOption='FORMATTED_VALUE'
        ).execute()
        
        # Process the spreadsheet content based on format
        if format == 'md':
            return convert_sheets_to_markdown(title, result, spreadsheet)
        elif format == 'html':
            return convert_sheets_to_html(title, result, spreadsheet)
        else:  # txt
            return convert_sheets_to_text(title, result, spreadsheet)
    except Exception as e:
        print(f"Error retrieving Google Sheet: {str(e)}")
        return None

def get_slides_document(doc_id, format='md', credentials=None):
    """Get a Google Slides document in the specified format."""
    if MOCK_MODE:
        if format == 'md':
            return f"# Mock Presentation\n\n## Slide 1\n\nTitle slide content\n\n## Slide 2\n\nContent slide with bullet points:\n\n* Point 1\n* Point 2\n* Point 3\n"
        elif format == 'html':
            return f"<html><body><h1>Mock Presentation</h1><h2>Slide 1</h2><p>Title slide content</p><h2>Slide 2</h2><p>Content slide with bullet points:</p><ul><li>Point 1</li><li>Point 2</li><li>Point 3</li></ul></body></html>"
        else:  # txt
            return f"Mock Presentation\n\nSlide 1\n\nTitle slide content\n\nSlide 2\n\nContent slide with bullet points:\n\nPoint 1\nPoint 2\nPoint 3"
    
    if credentials is None:
        credentials = get_credentials()
    
    service = build('slides', 'v1', credentials=credentials)
    
    try:
        # Get presentation content
        presentation = service.presentations().get(presentationId=doc_id).execute()
        
        # Process the presentation content based on format
        if format == 'md':
            return convert_slides_to_markdown(presentation)
        elif format == 'html':
            return convert_slides_to_html(presentation)
        else:  # txt
            return convert_slides_to_text(presentation)
    except Exception as e:
        print(f"Error retrieving Google Slides: {str(e)}")
        return None

def get_generic_document(doc_id, format='md', credentials=None):
    """Get a generic Google Drive document in the specified format."""
    if MOCK_MODE:
        return f"Mock generic document content for {doc_id} in {format} format"
    
    if credentials is None:
        credentials = get_credentials()
    
    service = build('drive', 'v3', credentials=credentials)
    
    try:
        # Export as HTML and convert to desired format
        response = service.files().export_media(
            fileId=doc_id,
            mimeType='text/html'
        ).execute()
        
        html_content = response.decode('utf-8')
        
        # Convert HTML to markdown
        h = html2text.HTML2Text()
        h.body_width = 0  # No wrapping
        markdown_content = h.handle(html_content)
        
        # Process content based on requested format
        if format == 'md':
            return markdown_content
        elif format == 'html':
            return html_content
        elif format == 'txt':
            # Simple text conversion (strip markdown)
            text_content = markdown_content
            # Remove headers
            text_content = re.sub(r'#+\s+', '', text_content)
            # Remove formatting
            text_content = re.sub(r'[\*_~`]', '', text_content)
            # Remove links but keep text
            text_content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text_content)
            return text_content
        else:
            return markdown_content  # Default to markdown
    except Exception as e:
        print(f"Error retrieving generic document: {str(e)}")
        return None

def get_sheet_ranges(spreadsheet):
    """Get all sheet ranges from a spreadsheet."""
    ranges = []
    for sheet in spreadsheet.get('sheets', []):
        sheet_name = sheet.get('properties', {}).get('title', '')
        if sheet_name:
            ranges.append(sheet_name)
    return ranges

def convert_doc_to_markdown(doc):
    """Convert a Google Doc to markdown format."""
    # For simplicity, we'll just return a basic conversion
    title = doc.get('title', 'Document')
    content = f"# {title}\n\n"
    
    # Add content from the document body
    for element in doc.get('body', {}).get('content', []):
        if 'paragraph' in element:
            para = element['paragraph']
            text = ""
            for element in para.get('elements', []):
                text += element.get('textRun', {}).get('content', '')
            content += text + "\n\n"
    
    return content

def convert_doc_to_html(doc):
    """Convert a Google Doc to HTML format."""
    # For simplicity, we'll just return a basic conversion
    title = doc.get('title', 'Document')
    content = f"<html><head><title>{title}</title></head><body><h1>{title}</h1>"
    
    # Add content from the document body
    for element in doc.get('body', {}).get('content', []):
        if 'paragraph' in element:
            para = element['paragraph']
            text = ""
            for element in para.get('elements', []):
                text += element.get('textRun', {}).get('content', '')
            content += f"<p>{text}</p>"
    
    content += "</body></html>"
    return content

def convert_doc_to_text(doc):
    """Convert a Google Doc to plain text format."""
    # For simplicity, we'll just return a basic conversion
    title = doc.get('title', 'Document')
    content = f"{title}\n\n"
    
    # Add content from the document body
    for element in doc.get('body', {}).get('content', []):
        if 'paragraph' in element:
            para = element['paragraph']
            text = ""
            for element in para.get('elements', []):
                text += element.get('textRun', {}).get('content', '')
            content += text + "\n\n"
    
    return content

def convert_sheets_to_markdown(title, result, spreadsheet):
    """Convert a Google Sheet to markdown format."""
    content = f"# {title}\n\n"
    
    # Process each sheet
    for value_range in result.get('valueRanges', []):
        sheet_name = value_range.get('range', '').split('!')[0].strip("'")
        values = value_range.get('values', [])
        
        if not values:
            continue
        
        content += f"## {sheet_name}\n\n"
        
        # Create markdown table
        header = values[0] if values else []
        if header:
            content += "| " + " | ".join(str(cell) for cell in header) + " |\n"
            content += "| " + " | ".join(["---"] * len(header)) + " |\n"
            
            for row in values[1:]:
                # Pad row if needed
                padded_row = row + [''] * (len(header) - len(row))
                content += "| " + " | ".join(str(cell) for cell in padded_row) + " |\n"
            
            content += "\n"
    
    return content

def convert_sheets_to_html(title, result, spreadsheet):
    """Convert a Google Sheet to HTML format."""
    content = f"<html><head><title>{title}</title></head><body><h1>{title}</h1>"
    
    # Process each sheet
    for value_range in result.get('valueRanges', []):
        sheet_name = value_range.get('range', '').split('!')[0].strip("'")
        values = value_range.get('values', [])
        
        if not values:
            continue
        
        content += f"<h2>{sheet_name}</h2>"
        
        # Create HTML table
        content += "<table border='1'>"
        
        header = values[0] if values else []
        if header:
            content += "<tr>" + "".join(f"<th>{cell}</th>" for cell in header) + "</tr>"
            
            for row in values[1:]:
                # Pad row if needed
                padded_row = row + [''] * (len(header) - len(row))
                content += "<tr>" + "".join(f"<td>{cell}</td>" for cell in padded_row) + "</tr>"
        
        content += "</table>"
    
    content += "</body></html>"
    return content

def convert_sheets_to_text(title, result, spreadsheet):
    """Convert a Google Sheet to plain text format."""
    content = f"{title}\n\n"
    
    # Process each sheet
    for value_range in result.get('valueRanges', []):
        sheet_name = value_range.get('range', '').split('!')[0].strip("'")
        values = value_range.get('values', [])
        
        if not values:
            continue
        
        content += f"{sheet_name}\n\n"
        
        # Create text table
        for row in values:
            content += " | ".join(str(cell) for cell in row) + "\n"
        
        content += "\n"
    
    return content

def convert_slides_to_markdown(presentation):
    """Convert a Google Slides presentation to markdown format."""
    title = presentation.get('title', 'Presentation')
    content = f"# {title}\n\n"
    
    # Process each slide
    for i, slide in enumerate(presentation.get('slides', []), 1):
        content += f"## Slide {i}\n\n"
        
        # Extract text from text elements
        for element in slide.get('pageElements', []):
            if 'shape' in element and 'text' in element['shape']:
                for textElement in element['shape']['text'].get('textElements', []):
                    if 'textRun' in textElement:
                        text = textElement['textRun'].get('content', '')
                        if text.strip():
                            content += text + "\n\n"
    
    return content

def convert_slides_to_html(presentation):
    """Convert a Google Slides presentation to HTML format."""
    title = presentation.get('title', 'Presentation')
    content = f"<html><head><title>{title}</title></head><body><h1>{title}</h1>"
    
    # Process each slide
    for i, slide in enumerate(presentation.get('slides', []), 1):
        content += f"<h2>Slide {i}</h2>"
        
        # Extract text from text elements
        for element in slide.get('pageElements', []):
            if 'shape' in element and 'text' in element['shape']:
                content += "<div class='slide-content'>"
                for textElement in element['shape']['text'].get('textElements', []):
                    if 'textRun' in textElement:
                        text = textElement['textRun'].get('content', '')
                        if text.strip():
                            content += f"<p>{text}</p>"
                content += "</div>"
    
    content += "</body></html>"
    return content

def convert_slides_to_text(presentation):
    """Convert a Google Slides presentation to plain text format."""
    title = presentation.get('title', 'Presentation')
    content = f"{title}\n\n"
    
    # Process each slide
    for i, slide in enumerate(presentation.get('slides', []), 1):
        content += f"Slide {i}\n\n"
        
        # Extract text from text elements
        for element in slide.get('pageElements', []):
            if 'shape' in element and 'text' in element['shape']:
                for textElement in element['shape']['text'].get('textElements', []):
                    if 'textRun' in textElement:
                        text = textElement['textRun'].get('content', '')
                        if text.strip():
                            content += text + "\n\n"
    
    return content

def get_document(doc_id, output_format='md'):
    """Get a Google Document and convert it to the specified format."""
    if MOCK_MODE:
        # Return mock data for testing
        if doc_id == '1hMxNtMh1_fB-tv0A6p4Wqza9hPp8sXcwMJNeQcbc54k':
            if output_format == 'md':
                return """# Test Spreadsheet

| Column A | Column B | Column C |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |
| Value 4  | Value 5  | Value 6  |
| Value 7  | Value 8  | Value 9  |

This is a mock spreadsheet for testing purposes.
"""
            elif output_format == 'html':
                return """<html>
<head><title>Test Spreadsheet</title></head>
<body>
<h1>Test Spreadsheet</h1>
<table>
<tr><th>Column A</th><th>Column B</th><th>Column C</th></tr>
<tr><td>Value 1</td><td>Value 2</td><td>Value 3</td></tr>
<tr><td>Value 4</td><td>Value 5</td><td>Value 6</td></tr>
<tr><td>Value 7</td><td>Value 8</td><td>Value 9</td></tr>
</table>
<p>This is a mock spreadsheet for testing purposes.</p>
</body>
</html>"""
            else:  # txt
                return """Test Spreadsheet

Column A | Column B | Column C
Value 1  | Value 2  | Value 3
Value 4  | Value 5  | Value 6
Value 7  | Value 8  | Value 9

This is a mock spreadsheet for testing purposes.
"""
        else:
            return f"Mock document content for {doc_id} in {output_format} format"
    
    # Get credentials and build the Drive API client
    credentials = get_credentials()
    
    # Extract the document type from the ID or fetch it
    doc_type = get_document_type(doc_id, credentials)
    
    if doc_type == 'document':
        return get_docs_document(doc_id, output_format, credentials)
    elif doc_type == 'spreadsheet':
        return get_sheets_document(doc_id, output_format, credentials)
    elif doc_type == 'presentation':
        return get_slides_document(doc_id, output_format, credentials)
    else:
        return get_generic_document(doc_id, output_format, credentials)

def search_document_content(doc_id, search_query):
    """Search for text within a document."""
    if MOCK_MODE:
        # Return mock search results for testing
        if search_query.lower() in "test spreadsheet column value mock":
            return [
                {
                    'context': f"This is a mock search result for '{search_query}' in the document.\n"
                              f"Line containing the query: 'This is a mock {search_query} for testing purposes.'"
                },
                {
                    'context': f"Another mock search result for '{search_query}'.\n"
                              f"Different context: 'The {search_query} appears here as well.'"
                }
            ]
        else:
            return []
    
    # Get the document content
    content = get_document(doc_id, output_format='txt')
    
    if not content:
        return []
    
    # Search for the query in the content
    results = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if search_query.lower() in line.lower():
            # Get context (3 lines before and after)
            start = max(0, i - 3)
            end = min(len(lines), i + 4)
            
            context = '\n'.join([
                f"{j+1}: {lines[j]}" for j in range(start, end)
            ])
            
            results.append({
                'context': context
            })
    
    return results
