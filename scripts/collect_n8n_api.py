#!/usr/bin/env python3
"""
Collect workflows from n8n official API
"""
import requests
import json
import os
from pathlib import Path
from hashlib import sha256

def collect_workflows():
    base_url = "https://api.n8n.io/templates/search"
    offset = 0
    limit = 100
    total_collected = 0

    Path("workflows/api").mkdir(parents=True, exist_ok=True)

    print("Starting n8n API collection...")

    while True:
        print(f"Fetching workflows (offset: {offset})...")
        response = requests.get(base_url, params={"limit": limit, "offset": offset})

        if response.status_code != 200:
            print(f"API request failed: {response.status_code}")
            break

        data = response.json()
        workflows = data.get('workflows', [])

        if not workflows:
            print("No more workflows to fetch")
            break

        for workflow in workflows:
            # Generate unique ID from workflow content
            workflow_hash = sha256(json.dumps(workflow, sort_keys=True).encode()).hexdigest()[:12]
            filename = f"workflows/api/{workflow_hash}.json"

            with open(filename, 'w') as f:
                json.dump(workflow, f, indent=2)

            total_collected += 1

        print(f"  Collected {len(workflows)} workflows (total: {total_collected})")
        offset += limit

    print(f"✅ Total collected: {total_collected} workflows")

if __name__ == "__main__":
    collect_workflows()
