#!/usr/bin/env python3
"""
GitHub utilities for TPM-CLI.
"""

import os
import json
import time
import requests
import sys
from datetime import datetime
from tabulate import tabulate
import re

# Import config utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config_utils import get_credential, set_credential

# Legacy paths for backward compatibility
GITHUB_TOKEN_FILE = os.path.expanduser("~/.config/github/token")
CACHE_DIR = os.path.expanduser("~/.tpm-cli/cache")

def setup_cache():
    """Set up the cache directory if it doesn't exist."""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR, exist_ok=True)

def get_github_token():
    """Get the GitHub token from the configuration."""
    # Try to get token from centralized config
    token = get_credential("github", "token")
    
    # If not found, try legacy path
    if not token and os.path.exists(GITHUB_TOKEN_FILE):
        try:
            with open(GITHUB_TOKEN_FILE, 'r') as f:
                token = f.read().strip()
                # Save to centralized config for future use
                set_credential("github", token, "token")
        except Exception as e:
            print(f"Error reading GitHub token from legacy path: {e}")
    
    return token

def search_repos(query, org=None, token=None, max_pages=None, match_type="contains"):
    """Search for repositories using GitHub's search API with pagination.
    
    If max_pages is None, fetch all available pages.
    
    Args:
        query: The search query string
        org: The GitHub organization to search in
        token: GitHub API token
        max_pages: Maximum number of pages to fetch (100 repos per page)
        match_type: How to match the query against repo names:
                   "contains" - query appears anywhere in the name
                   "prefix" - query is a prefix of the name
                   "suffix" - query is a suffix of the name
                   "exact" - query exactly matches the name
    """
    if not token:
        token = get_github_token()
    
    if not token:
        raise Exception("GitHub token not found. Please set up your GitHub token.")
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Construct the search query
    if match_type == "exact":
        search_query = f"{query} in:name"
    elif match_type == "prefix":
        search_query = f"{query} in:name"
    elif match_type == "suffix":
        search_query = f"{query} in:name"
    else:  # contains
        search_query = f"{query} in:name"
    
    if org:
        search_query = f"org:{org} {search_query}"
    
    url = f"https://api.github.com/search/repositories?q={search_query}&per_page=100"
    
    all_repos = []
    page = 1
    
    while True:
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"GitHub API error: {response.status_code} - {response.text}")
        
        data = response.json()
        repos = data.get("items", [])
        all_repos.extend(repos)
        
        # Check if we've reached the maximum number of pages
        if max_pages and page >= max_pages:
            break
        
        # Check if there are more pages
        if "next" not in response.links:
            break
        
        # Get the URL for the next page
        url = response.links["next"]["url"]
        page += 1
        
        # Be nice to the GitHub API and avoid rate limiting
        time.sleep(1)
    
    # Filter results based on match_type if needed
    filtered_repos = []
    for repo in all_repos:
        repo_name = repo["name"].lower()
        query_lower = query.lower()
        
        if match_type == "exact" and repo_name == query_lower:
            filtered_repos.append(repo)
        elif match_type == "prefix" and repo_name.startswith(query_lower):
            filtered_repos.append(repo)
        elif match_type == "suffix" and repo_name.endswith(query_lower):
            filtered_repos.append(repo)
        elif match_type == "contains" and query_lower in repo_name:
            filtered_repos.append(repo)
    
    return filtered_repos

def classify_repository(repo):
    """Classify repository based on name, description, size, and activity."""
    # Default classification
    classification = {
        "type": "Unknown",
        "activity": "Unknown",
        "importance": "Unknown"
    }
    
    # Repository type classification based on name and description
    name = repo["name"].lower()
    description = (repo.get("description") or "").lower()
    
    # Type classification
    if any(x in name for x in ["api", "service", "backend"]) or any(x in description for x in ["api", "service", "backend"]):
        classification["type"] = "Backend Service"
    elif any(x in name for x in ["ui", "frontend", "web"]) or any(x in description for x in ["ui", "frontend", "web"]):
        classification["type"] = "Frontend Application"
    elif any(x in name for x in ["lib", "library", "sdk"]) or any(x in description for x in ["library", "sdk"]):
        classification["type"] = "Library"
    elif any(x in name for x in ["tool", "utility"]) or any(x in description for x in ["tool", "utility"]):
        classification["type"] = "Tool"
    elif any(x in name for x in ["doc", "docs", "documentation"]) or any(x in description for x in ["documentation"]):
        classification["type"] = "Documentation"
    elif any(x in name for x in ["test", "testing"]) or any(x in description for x in ["test framework", "testing"]):
        classification["type"] = "Testing"
    
    # Activity classification based on pushed_at date
    if "pushed_at" in repo:
        pushed_at = datetime.strptime(repo["pushed_at"], "%Y-%m-%dT%H:%M:%SZ")
        now = datetime.utcnow()
        days_since_last_push = (now - pushed_at).days
        
        if days_since_last_push <= 30:
            classification["activity"] = "Active"
        else:
            classification["activity"] = "Inactive"
    
    # Importance classification based on stars, forks, and size
    stars = repo.get("stargazers_count", 0)
    forks = repo.get("forks_count", 0)
    size = repo.get("size", 0)
    
    importance_score = stars * 3 + forks * 5 + size / 1000
    
    if importance_score > 50:
        classification["importance"] = "High"
    elif importance_score > 10:
        classification["importance"] = "Medium"
    else:
        classification["importance"] = "Low"
    
    return classification

def get_repo_details(repo_data, org, token=None):
    """Get additional details for a repository."""
    if not token:
        token = get_github_token()
    
    if not token:
        raise Exception("GitHub token not found. Please set up your GitHub token.")
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Get repository details
    repo_url = f"https://api.github.com/repos/{org}/{repo_data['name']}"
    response = requests.get(repo_url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"GitHub API error: {response.status_code} - {response.text}")
    
    repo = response.json()
    
    # Get contributors
    contributors_url = f"{repo_url}/contributors"
    response = requests.get(contributors_url, headers=headers)
    
    contributors = []
    if response.status_code == 200:
        contributors = response.json()
    
    # Get languages
    languages_url = f"{repo_url}/languages"
    response = requests.get(languages_url, headers=headers)
    
    languages = {}
    if response.status_code == 200:
        languages = response.json()
    
    return {
        "repo": repo,
        "contributors": contributors,
        "languages": languages
    }

def format_date(date_str):
    """Format a date string to a more readable format."""
    if not date_str:
        return "N/A"
    
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return date_obj.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return date_str
