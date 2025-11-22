#!/usr/bin/env python3
"""
Script to process evidence files by calculating SHA-256 hashes and moving them to the hashed directory.

This script:
1. Scans the evidence/raw/ directory for new files
2. Calculates SHA-256 hashes for each file
3. Updates the manifest.json with file information and hashes
4. Moves the files from evidence/raw/ to evidence/hashed/
"""

import hashlib
import json
import os
import shutil
from pathlib import Path
from datetime import datetime, timezone


def calculate_sha256(filepath):
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read the file in chunks to handle large files efficiently
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def load_manifest(manifest_path):
    """Load existing manifest or create a new one."""
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r') as f:
            return json.load(f)
    return {"files": [], "metadata": {"created": datetime.now(timezone.utc).isoformat()}}


def save_manifest(manifest_path, manifest):
    """Save manifest to JSON file."""
    manifest["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)


def process_evidence_files():
    """Main function to process evidence files."""
    # Define paths
    base_dir = Path(__file__).parent.parent
    raw_dir = base_dir / "evidence" / "raw"
    hashed_dir = base_dir / "evidence" / "hashed"
    manifest_path = base_dir / "evidence" / "manifest.json"
    
    # Ensure directories exist
    raw_dir.mkdir(parents=True, exist_ok=True)
    hashed_dir.mkdir(parents=True, exist_ok=True)
    
    # Load manifest
    manifest = load_manifest(manifest_path)
    
    # Get list of already processed files
    processed_files = {entry["original_filename"] for entry in manifest.get("files", [])}
    
    # Find new files in raw directory
    new_files = []
    for file_path in raw_dir.iterdir():
        # Skip .gitkeep and other hidden files
        if file_path.is_file() and not file_path.name.startswith('.') and file_path.name not in processed_files:
            new_files.append(file_path)
    
    if not new_files:
        print("No new files to process.")
        return
    
    print(f"Found {len(new_files)} new file(s) to process:")
    
    # Process each new file
    for file_path in new_files:
        print(f"\nProcessing: {file_path.name}")
        
        # Calculate SHA-256 hash
        file_hash = calculate_sha256(file_path)
        print(f"  SHA-256: {file_hash}")
        
        # Create hashed filename
        file_extension = file_path.suffix
        hashed_filename = f"{file_hash}{file_extension}"
        hashed_path = hashed_dir / hashed_filename
        
        # Move file to hashed directory
        shutil.move(str(file_path), str(hashed_path))
        print(f"  Moved to: evidence/hashed/{hashed_filename}")
        
        # Add entry to manifest
        file_entry = {
            "original_filename": file_path.name,
            "hashed_filename": hashed_filename,
            "sha256": file_hash,
            "size_bytes": os.path.getsize(hashed_path),
            "processed_date": datetime.now(timezone.utc).isoformat(),
            "path": f"evidence/hashed/{hashed_filename}"
        }
        manifest.setdefault("files", []).append(file_entry)
    
    # Save updated manifest
    save_manifest(manifest_path, manifest)
    print(f"\nManifest updated: {manifest_path}")
    print(f"Total files in manifest: {len(manifest['files'])}")


if __name__ == "__main__":
    process_evidence_files()
