#!/usr/bin/env python3
"""
GitHub commands for TPM-CLI.
"""

import os
import sys
import json
from tabulate import tabulate
from datetime import datetime
import github_utils

def cmd_repo(args):
    """Find repositories or get repository information."""
    try:
        # Get GitHub token
        token = github_utils.get_github_token()
        if not token:
            print("GitHub token not found. Please set up your GitHub token.")
            sys.exit(1)
        
        # Search for repositories
        match_type = "exact" if args.query.count("/") == 0 and " " not in args.query else "contains"
        max_pages = args.max_pages if args.limit_pages else None
        
        repos = github_utils.search_repos(
            args.query, 
            org=args.org, 
            token=token, 
            max_pages=max_pages,
            match_type=match_type
        )
        
        if not repos:
            print(f"No repositories found matching '{args.query}' in {args.org}.")
            sys.exit(0)
        
        # If only one repo is found or details are requested, get additional details
        if len(repos) == 1 or args.details:
            detailed_results = []
            
            for repo in repos:
                details = github_utils.get_repo_details(repo, args.org, token)
                detailed_repo = details["repo"]
                contributors = details["contributors"]
                languages = details["languages"]
                
                # Calculate language percentages
                total_bytes = sum(languages.values())
                language_percentages = {}
                if total_bytes > 0:
                    for lang, bytes_count in languages.items():
                        language_percentages[lang] = round((bytes_count / total_bytes) * 100, 2)
                
                # Format top contributors
                top_contributors = []
                for contributor in contributors[:5]:  # Show top 5 contributors
                    top_contributors.append(f"{contributor['login']} ({contributor['contributions']})")
                
                detailed_results.append({
                    "name": detailed_repo["name"],
                    "url": detailed_repo["html_url"],
                    "description": detailed_repo["description"] or "No description",
                    "created_at": github_utils.format_date(detailed_repo.get("created_at")),
                    "updated_at": github_utils.format_date(detailed_repo.get("updated_at")),
                    "pushed_at": github_utils.format_date(detailed_repo.get("pushed_at")),
                    "stars": detailed_repo.get("stargazers_count", 0),
                    "forks": detailed_repo.get("forks_count", 0),
                    "open_issues": detailed_repo.get("open_issues_count", 0),
                    "language": detailed_repo.get("language", "None"),
                    "languages": language_percentages,
                    "contributors": top_contributors,
                    "size": detailed_repo.get("size", 0),
                    "default_branch": detailed_repo.get("default_branch", "main"),
                    "license": detailed_repo.get("license", {}).get("name", "None"),
                    "classification": github_utils.classify_repository(detailed_repo)
                })
            
            # Output detailed results
            if args.output:
                with open(args.output, 'w') as f:
                    f.write("# Repository Details\n\n")
                    
                    for result in detailed_results:
                        f.write(f"## {result['name']}\n\n")
                        f.write(f"**URL:** {result['url']}  \n")
                        f.write(f"**Description:** {result['description']}  \n")
                        f.write(f"**Created:** {result['created_at']}  \n")
                        f.write(f"**Last Updated:** {result['updated_at']}  \n")
                        f.write(f"**Last Push:** {result['pushed_at']}  \n")
                        f.write(f"**Stars:** {result['stars']}  \n")
                        f.write(f"**Forks:** {result['forks']}  \n")
                        f.write(f"**Open Issues:** {result['open_issues']}  \n")
                        f.write(f"**Primary Language:** {result['language']}  \n")
                        f.write(f"**Size:** {result['size']} KB  \n")
                        f.write(f"**Default Branch:** {result['default_branch']}  \n")
                        f.write(f"**License:** {result['license']}  \n")
                        f.write(f"**Type:** {result['classification']['type']}  \n")
                        f.write(f"**Activity:** {result['classification']['activity']}  \n")
                        f.write(f"**Importance:** {result['classification']['importance']}  \n\n")
                        
                        # Languages
                        f.write("### Languages\n\n")
                        for lang, percentage in result['languages'].items():
                            f.write(f"- {lang}: {percentage}%  \n")
                        f.write("\n")
                        
                        # Contributors
                        f.write("### Top Contributors\n\n")
                        for contributor in result['contributors']:
                            f.write(f"- {contributor}  \n")
                        f.write("\n")
                
                print(f"Detailed results saved to {args.output}")
            else:
                for result in detailed_results:
                    print(f"\n{'-' * 80}")
                    print(f"Repository: {result['name']}")
                    print(f"URL: {result['url']}")
                    print(f"Description: {result['description']}")
                    print(f"Created: {result['created_at']}")
                    print(f"Last Updated: {result['updated_at']}")
                    print(f"Last Push: {result['pushed_at']}")
                    print(f"Stars: {result['stars']}")
                    print(f"Forks: {result['forks']}")
                    print(f"Open Issues: {result['open_issues']}")
                    print(f"Primary Language: {result['language']}")
                    print(f"Size: {result['size']} KB")
                    print(f"Default Branch: {result['default_branch']}")
                    print(f"License: {result['license']}")
                    print(f"Type: {result['classification']['type']}")
                    print(f"Activity: {result['classification']['activity']}")
                    print(f"Importance: {result['classification']['importance']}")
                    
                    print("\nLanguages:")
                    for lang, percentage in result['languages'].items():
                        print(f"- {lang}: {percentage}%")
                    
                    print("\nTop Contributors:")
                    for contributor in result['contributors']:
                        print(f"- {contributor}")
                    
                    print(f"{'-' * 80}")
        else:
            # Apply filters if specified
            filtered_repos = repos
            
            if args.type:
                filtered_repos = [repo for repo in filtered_repos if github_utils.classify_repository(repo)["type"] == args.type]
            
            if args.activity:
                filtered_repos = [repo for repo in filtered_repos if github_utils.classify_repository(repo)["activity"] == args.activity]
            
            if args.importance:
                filtered_repos = [repo for repo in filtered_repos if github_utils.classify_repository(repo)["importance"] == args.importance]
            
            # Prepare table data
            table_data = []
            for repo in filtered_repos:
                classification = github_utils.classify_repository(repo)
                table_data.append([
                    repo["name"],
                    repo.get("description", "")[:50] + ("..." if repo.get("description", "") and len(repo.get("description", "")) > 50 else ""),
                    repo.get("language", ""),
                    repo.get("stargazers_count", 0),
                    repo.get("forks_count", 0),
                    github_utils.format_date(repo.get("pushed_at", "")),
                    classification["type"],
                    classification["activity"],
                    classification["importance"]
                ])
            
            # Sort by name
            table_data.sort(key=lambda x: x[0])
            
            # Output table
            headers = ["Name", "Description", "Language", "Stars", "Forks", "Last Push", "Type", "Activity", "Importance"]
            table = tabulate(table_data, headers=headers, tablefmt="grid")
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(f"# Repositories matching '{args.query}' in {args.org}\n\n")
                    f.write("| " + " | ".join(headers) + " |\n")
                    f.write("| " + " | ".join(["---"] * len(headers)) + " |\n")
                    
                    for row in table_data:
                        f.write("| " + " | ".join(str(cell) for cell in row) + " |\n")
                
                print(f"Results saved to {args.output}")
            else:
                print(f"\nFound {len(filtered_repos)} repositories matching '{args.query}' in {args.org}:")
                print(table)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
