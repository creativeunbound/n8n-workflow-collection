#!/usr/bin/env python3
"""
Build searchable index from collected workflows and generate README
"""
import json
from pathlib import Path
from datetime import datetime
from collections import Counter

def extract_metadata(workflow_data):
    """Extract searchable metadata from workflow JSON"""
    nodes = workflow_data.get('nodes', [])

    # Extract integrations (node types)
    integrations = list(set([
        node.get('type', '').replace('n8n-nodes-base.', '')
        for node in nodes
        if node.get('type')
    ]))

    # Calculate complexity
    node_count = len(nodes)
    if node_count <= 5:
        complexity = 'beginner'
    elif node_count <= 15:
        complexity = 'intermediate'
    else:
        complexity = 'advanced'

    return {
        'node_count': node_count,
        'integrations': integrations,
        'complexity': complexity
    }

def build_index():
    index = []

    print("Building index...")

    # Process API workflows
    api_dir = Path('workflows/api')
    if api_dir.exists():
        for json_file in api_dir.glob('*.json'):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)

                metadata = extract_metadata(data)

                index.append({
                    'id': json_file.stem,
                    'source': 'n8n_api',
                    'title': data.get('name', 'Untitled'),
                    'description': data.get('description', ''),
                    'author': data.get('user', {}).get('username', 'unknown'),
                    'views': data.get('views', 0),
                    'file': str(json_file),
                    **metadata
                })
            except Exception as e:
                print(f"  ⚠️  Error processing {json_file.name}: {e}")

    # Process GitHub workflows
    github_dir = Path('workflows/github')
    if github_dir.exists():
        for json_file in github_dir.glob('*.json'):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)

                metadata = extract_metadata(data)
                source_info = data.get('_source', {})

                index.append({
                    'id': json_file.stem,
                    'source': 'github',
                    'source_repo': source_info.get('repo', 'unknown'),
                    'title': data.get('name', 'Untitled'),
                    'description': data.get('notes', ''),
                    'file': str(json_file),
                    **metadata
                })
            except Exception as e:
                print(f"  ⚠️  Error processing {json_file.name}: {e}")

    # Sort by node count (proxy for complexity/value)
    index.sort(key=lambda x: x['node_count'], reverse=True)

    # Write index
    with open('index.json', 'w') as f:
        json.dump({
            'updated_at': datetime.now().isoformat(),
            'total_workflows': len(index),
            'workflows': index
        }, f, indent=2)

    # Generate README stats
    generate_readme(index)

    print(f"✅ Index built: {len(index)} workflows")

def generate_readme(index):
    total = len(index)
    api_count = sum(1 for w in index if w['source'] == 'n8n_api')
    github_count = sum(1 for w in index if w['source'] == 'github')

    # Count by complexity
    beginner = sum(1 for w in index if w['complexity'] == 'beginner')
    intermediate = sum(1 for w in index if w['complexity'] == 'intermediate')
    advanced = sum(1 for w in index if w['complexity'] == 'advanced')

    # Top integrations
    all_integrations = []
    for w in index:
        all_integrations.extend(w['integrations'])

    top_integrations = Counter(all_integrations).most_common(10)

    readme = f"""# n8n Workflow Collection

Automated collection of {total:,} n8n workflows from the official API and community GitHub repositories.

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

## Collection Stats

- **Total Workflows:** {total:,}
  - From n8n Official API: {api_count:,}
  - From GitHub Repos: {github_count:,}

- **By Complexity:**
  - Beginner (1-5 nodes): {beginner:,}
  - Intermediate (6-15 nodes): {intermediate:,}
  - Advanced (16+ nodes): {advanced:,}

## Top Integrations

"""

    for integration, count in top_integrations:
        readme += f"- **{integration}**: {count:,} workflows\n"

    readme += """

## Browse Workflows

See `index.json` for full searchable metadata, or browse:
- `workflows/api/` - Workflows from n8n official marketplace
- `workflows/github/` - Workflows from community GitHub repos

## Automation

This collection is automatically updated weekly via GitHub Actions:
- **Mondays:** Discover new GitHub repos
- **Tuesdays:** Collect from n8n API
- **Wednesdays:** Extract from GitHub repos

## License

Individual workflows retain their original licenses. This collection repo is MIT licensed.
"""

    with open('README.md', 'w') as f:
        f.write(readme)

    print("✅ README.md generated")

if __name__ == "__main__":
    build_index()
