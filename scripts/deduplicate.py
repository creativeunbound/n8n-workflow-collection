#!/usr/bin/env python3
"""
Deduplicate workflow files based on content hash
"""
import json
import os
from pathlib import Path
from hashlib import sha256
import sys

def deduplicate(directory):
    seen_hashes = set()
    duplicates = []

    print(f"Deduplicating workflows in {directory}...")

    for json_file in Path(directory).glob('*.json'):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)

            # Remove source metadata for hash calculation
            data_copy = data.copy()
            data_copy.pop('_source', None)

            file_hash = sha256(json.dumps(data_copy, sort_keys=True).encode()).hexdigest()

            if file_hash in seen_hashes:
                duplicates.append(json_file)
            else:
                seen_hashes.add(file_hash)
        except Exception as e:
            print(f"  ⚠️  Error processing {json_file.name}: {e}")

    # Remove duplicates
    for dup in duplicates:
        os.remove(dup)
        print(f"  Removed duplicate: {dup.name}")

    print(f"✅ Removed {len(duplicates)} duplicates, {len(seen_hashes)} unique workflows remain")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python deduplicate.py <directory>")
        sys.exit(1)

    deduplicate(sys.argv[1])
