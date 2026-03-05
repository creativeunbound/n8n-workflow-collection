#!/usr/bin/env python3
"""
Extract n8n workflows from GitHub repos using API (no cloning)
"""
import json
import requests
import os
from pathlib import Path
from hashlib import sha256
import time

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

def parse_github_url(url):
    """Extract owner and repo from GitHub URL"""
    # https://github.com/owner/repo → owner, repo
    parts = url.rstrip('/').split('/')
    return parts[-2], parts[-1]

def search_json_files(owner, repo):
    """Search for .json files in a repo using GitHub Code Search API"""
    search_url = "https://api.github.com/search/code"
    params = {
        'q': f'extension:json repo:{owner}/{repo}',
        'per_page': 100
    }
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}

    response = requests.get(search_url, params=params, headers=headers)

    if response.status_code != 200:
        print(f"  ⚠️  Search failed: {response.status_code}")
        return []

    return response.json().get('items', [])

def download_workflow(file_info, repo_url):
    """Download and validate a workflow file"""
    # Get raw content URL
    raw_url = file_info['html_url'].replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')

    try:
        response = requests.get(raw_url, timeout=10)
        if response.status_code != 200:
            return None

        data = response.json()

        # Validate: must have "nodes" array
        if not isinstance(data, dict) or 'nodes' not in data:
            return None

        # Add source metadata
        data['_source'] = {
            'repo': repo_url,
            'file': file_info['path']
        }

        return data

    except Exception as e:
        print(f"  ⚠️  Failed to download {file_info['path']}: {e}")
        return None

def extract_workflows():
    with open('discovered-repos.json', 'r') as f:
        repos = json.load(f)

    Path("workflows/github").mkdir(parents=True, exist_ok=True)
    total_extracted = 0

    print("Starting GitHub workflow extraction...")

    # Process top 10 repos by stars
    sorted_repos = sorted(repos, key=lambda x: x.get('stargazersCount', 0), reverse=True)[:10]

    for repo in sorted_repos:
        repo_url = repo['url']
        repo_name = repo['name']
        stars = repo.get('stargazersCount', 0)

        print(f"Processing: {repo_name} ({stars} stars)")

        try:
            owner, repo_slug = parse_github_url(repo_url)
        except Exception as e:
            print(f"  ⚠️  Failed to parse URL: {e}")
            continue

        # Search for JSON files
        json_files = search_json_files(owner, repo_slug)
        print(f"  Found {len(json_files)} JSON files")

        for file_info in json_files:
            workflow_data = download_workflow(file_info, repo_url)

            if workflow_data:
                # Generate unique filename
                workflow_hash = sha256(json.dumps(workflow_data, sort_keys=True).encode()).hexdigest()[:12]
                output_file = f"workflows/github/{workflow_hash}.json"

                with open(output_file, 'w') as f:
                    json.dump(workflow_data, f, indent=2)

                total_extracted += 1
                print(f"  ✅ Extracted: {file_info['name']}")

        # Rate limiting: GitHub Code Search API is 10 req/min
        # Wait 6 seconds between repos to stay under limit
        time.sleep(6)

    print(f"✅ Total extracted: {total_extracted} workflows")

if __name__ == "__main__":
    extract_workflows()
