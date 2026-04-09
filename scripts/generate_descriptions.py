#!/usr/bin/env python3
"""
Auto-generate short descriptions for n8n workflows based on their metadata.
Reads workflow JSON files and updates index.json with generated descriptions.
"""
import json
import re
from pathlib import Path

# Node types to human-readable names
NODE_NAMES = {
    # Triggers
    "webhook": "Webhook",
    "scheduleTrigger": "Schedule",
    "cron": "Cron",
    "manualTrigger": "Manual",
    "emailTrigger": "Email Trigger",
    "formTrigger": "Form",
    "@n8n/n8n-nodes-langchain.chatTrigger": "Chat",
    # Services
    "googleSheets": "Google Sheets",
    "googleDrive": "Google Drive",
    "googleCalendar": "Google Calendar",
    "gmail": "Gmail",
    "slack": "Slack",
    "discord": "Discord",
    "telegram": "Telegram",
    "whatsapp": "WhatsApp",
    "notion": "Notion",
    "airtable": "Airtable",
    "postgres": "PostgreSQL",
    "mysql": "MySQL",
    "redis": "Redis",
    "supabase": "Supabase",
    "mongodb": "MongoDB",
    "httpRequest": "HTTP Request",
    "openAi": "OpenAI",
    "@n8n/n8n-nodes-langchain.openAi": "OpenAI",
    "@n8n/n8n-nodes-langchain.lmChatOpenAi": "OpenAI Chat",
    "@n8n/n8n-nodes-langchain.agent": "AI Agent",
    "@n8n/n8n-nodes-langchain.chainLlm": "LLM Chain",
    "@n8n/n8n-nodes-langchain.lmChatAnthropic": "Anthropic",
    "@n8n/n8n-nodes-langchain.lmChatGroq": "Groq",
    "@n8n/n8n-nodes-langchain.lmChatOllama": "Ollama",
    "@n8n/n8n-nodes-langchain.memoryBufferWindow": "Buffer Memory",
    "@n8n/n8n-nodes-langchain.memoryPostgresChat": "Postgres Memory",
    "@n8n/n8n-nodes-langchain.vectorStoreSupabase": "Supabase Vector Store",
    "@n8n/n8n-nodes-langchain.vectorStorePinecone": "Pinecone Vector Store",
    "@n8n/n8n-nodes-langchain.embeddingsOpenAi": "OpenAI Embeddings",
    "@n8n/n8n-nodes-langchain.toolWorkflow": "Workflow Tool",
    "@n8n/n8n-nodes-langchain.toolVectorStore": "Vector Store Tool",
    "@n8n/n8n-nodes-langchain.outputParserStructured": "Structured Output Parser",
    "@n8n/n8n-nodes-langchain.textClassifier": "Text Classifier",
    "@n8n/n8n-nodes-langchain.informationExtractor": "Information Extractor",
    "@n8n/n8n-nodes-langchain.documentDefaultDataLoader": "Document Loader",
    "@n8n/n8n-nodes-langchain.textSplitterCharacterTextSplitter": "Text Splitter",
    "n8n-nodes-evolution-api.evolutionApi": "Evolution API",
    "github": "GitHub",
    "jira": "Jira",
    "trello": "Trello",
    "asana": "Asana",
    "hubspot": "HubSpot",
    "salesforce": "Salesforce",
    "stripe": "Stripe",
    "shopify": "Shopify",
    "wooCommerce": "WooCommerce",
    "twitter": "Twitter/X",
    "facebookGraph": "Facebook",
    "linkedIn": "LinkedIn",
    "dropbox": "Dropbox",
    "aws": "AWS",
    "s3": "AWS S3",
    "microsoftOutlook": "Outlook",
    "microsoftTeams": "Microsoft Teams",
    "microsoftExcel": "Excel",
    "sendGrid": "SendGrid",
    "mailchimp": "Mailchimp",
    "twilio": "Twilio",
    "wordpress": "WordPress",
    "googleAnalytics": "Google Analytics",
    "rss": "RSS",
    "rssFeedRead": "RSS Feed",
    "xml": "XML",
    "html": "HTML",
    "csv": "CSV",
    "spreadsheetFile": "Spreadsheet",
    "convertToFile": "File Converter",
    "extractFromFile": "File Extractor",
    "ftp": "FTP",
    "ssh": "SSH",
    "executeCommand": "Shell Command",
    "crypto": "Crypto",
    "dateTime": "DateTime",
    "wait": "Wait",
}

# Utility/flow nodes to exclude from description
UTILITY_NODES = {
    "set", "if", "switch", "merge", "splitInBatches", "splitOut",
    "aggregate", "noOp", "stickyNote", "code", "function",
    "functionItem", "itemLists", "sort", "limit", "removeDuplicates",
    "renameKeys", "respondToWebhook", "executeWorkflow", "errorTrigger",
    "start", "manualTrigger", "filter",
}

# Trigger node patterns
TRIGGER_PATTERNS = [
    "Trigger", "trigger", "webhook", "Webhook", "cron", "Cron",
    "scheduleTrigger", "chatTrigger", "formTrigger",
]


def is_trigger_node(node_type):
    """Check if a node type is a trigger."""
    return any(p in node_type for p in TRIGGER_PATTERNS)


def get_human_name(node_type):
    """Convert node type identifier to human-readable name."""
    if node_type in NODE_NAMES:
        return NODE_NAMES[node_type]
    # Strip common prefixes
    clean = node_type.replace("n8n-nodes-base.", "").replace("@n8n/n8n-nodes-langchain.", "")
    # camelCase to Title Case
    words = re.sub(r'([A-Z])', r' \1', clean).strip()
    return words.title()


def extract_sticky_note_summary(workflow_data):
    """Extract a short summary from sticky note content if available."""
    nodes = workflow_data.get("nodes", [])
    for node in nodes:
        node_type = node.get("type", "")
        if "stickyNote" in node_type:
            content = node.get("parameters", {}).get("content", "")
            if content:
                # Take first line, strip markdown
                first_line = content.strip().split("\n")[0]
                first_line = re.sub(r'[#*_`\[\]]', '', first_line).strip()
                if 20 < len(first_line) < 200:
                    return first_line
    return None


def generate_description(workflow_entry, workflow_data):
    """Generate a short description for a workflow."""
    nodes = workflow_data.get("nodes", [])
    if not nodes:
        return ""

    # Try sticky note summary first
    sticky_summary = extract_sticky_note_summary(workflow_data)
    if sticky_summary:
        return sticky_summary

    # Identify triggers
    triggers = []
    integrations = []

    for node in nodes:
        node_type = node.get("type", "").replace("n8n-nodes-base.", "")
        if not node_type:
            continue

        if is_trigger_node(node_type):
            name = get_human_name(node_type)
            if name not in triggers:
                triggers.append(name)
        elif node_type not in UTILITY_NODES and "stickyNote" not in node_type:
            name = get_human_name(node_type)
            if name not in integrations:
                integrations.append(name)

    # Build description
    parts = []

    # Trigger prefix — avoid "Trigger-triggered" redundancy
    if triggers:
        trigger = triggers[0]
        if trigger.endswith(" Trigger"):
            trigger = trigger[:-8]
        parts.append(f"{trigger}-triggered")
    else:
        parts.append("Automated")

    # Core integrations (top 3)
    if integrations:
        top = integrations[:3]
        if len(top) == 1:
            parts.append(f"workflow using {top[0]}")
        elif len(top) == 2:
            parts.append(f"workflow using {top[0]} and {top[1]}")
        else:
            parts.append(f"workflow using {', '.join(top[:2])}, and {top[2]}")
    else:
        parts.append("workflow")

    # Suffix with stats
    node_count = workflow_entry.get("node_count", len(nodes))
    complexity = workflow_entry.get("complexity", "intermediate")
    desc = " ".join(parts) + f" ({node_count} nodes, {complexity})"

    return desc


def main():
    index_path = Path("index.json")
    if not index_path.exists():
        print("❌ index.json not found")
        return

    with open(index_path, "r") as f:
        index = json.load(f)

    workflows = index.get("workflows", [])
    updated = 0

    for entry in workflows:
        # Skip if description already exists
        if entry.get("description", "").strip():
            continue

        # Load the raw workflow file
        workflow_file = Path(entry.get("file", ""))
        if not workflow_file.exists():
            continue

        try:
            with open(workflow_file, "r") as f:
                workflow_data = json.load(f)
        except Exception as e:
            print(f"  ⚠️  Error reading {workflow_file}: {e}")
            continue

        description = generate_description(entry, workflow_data)
        if description:
            entry["description"] = description
            updated += 1

    # Write updated index
    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)

    print(f"✅ Generated descriptions for {updated} workflows")


if __name__ == "__main__":
    main()
