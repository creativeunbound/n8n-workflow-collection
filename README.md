# n8n Workflow Collection

Automated collection of n8n workflows from the official API and community GitHub repositories.

**Status:** Initial setup complete. Automated collection will begin on first scheduled run.

## What This Is

This repository automatically discovers, collects, and organizes n8n workflow templates from:
- **n8n Official API** - Templates from the official n8n marketplace
- **GitHub Repositories** - Community-contributed workflows from public repos

## Automation Schedule

Workflows are collected automatically via GitHub Actions:
- **Mondays 3 AM UTC:** Discover new GitHub repositories with n8n workflows
- **Tuesdays 3 AM UTC:** Collect workflows from n8n official API
- **Wednesdays 3 AM UTC:** Extract workflows from discovered GitHub repos

## Repository Structure

```
workflows/
├── api/       # Workflows from n8n official API
└── github/    # Workflows from community GitHub repos

index.json     # Searchable metadata for all workflows
discovered-repos.json  # List of tracked GitHub repositories
README.md      # This file (auto-updated with stats)
```

## Browse Workflows

Once collection begins, you can:
- Browse `workflows/api/` and `workflows/github/` directories
- Search `index.json` for workflows by integration, complexity, or keyword
- View auto-generated statistics in this README

## Collection Methods

- **No cloning:** Workflows are downloaded directly via APIs (no disk bloat)
- **Deduplicated:** Identical workflows are detected and removed
- **Metadata extraction:** Node count, integrations, and complexity automatically calculated
- **Legal compliance:** Proper attribution and licensing preserved

## License

This collection repository is MIT licensed. Individual workflows retain their original licenses.

---

**Repository:** https://github.com/creativeunbound/n8n-workflow-collection
**Automation:** GitHub Actions (free tier)
**Update Frequency:** Weekly
