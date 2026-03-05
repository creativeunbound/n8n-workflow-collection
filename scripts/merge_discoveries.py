#!/usr/bin/env python3
"""
Merge new repo discoveries with existing list, avoiding duplicates
"""
import json
import sys

def merge_discoveries(new_file, existing_file):
    with open(new_file, 'r') as f:
        new_repos = json.load(f)

    try:
        with open(existing_file, 'r') as f:
            existing_repos = json.load(f)
    except FileNotFoundError:
        existing_repos = []

    # Create set of existing URLs for fast lookup
    existing_urls = {repo['url'] for repo in existing_repos}

    # Add new repos that don't exist yet
    added = 0
    for repo in new_repos:
        if repo['url'] not in existing_urls:
            existing_repos.append(repo)
            added += 1

    print(f"Added {added} new repositories", file=sys.stderr)

    # Sort by stars descending
    existing_repos.sort(key=lambda x: x.get('stargazersCount', 0), reverse=True)

    # Output merged list
    print(json.dumps(existing_repos, indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python merge_discoveries.py <new_file> <existing_file>", file=sys.stderr)
        sys.exit(1)

    merge_discoveries(sys.argv[1], sys.argv[2])
