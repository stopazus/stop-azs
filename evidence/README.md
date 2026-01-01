# Evidence Directory

This directory contains the evidence file processing system for the stop-azs repository.

## Directory Structure

- **raw/** - Place new evidence files here for processing
- **hashed/** - Contains processed files renamed with their SHA-256 hash
- **manifest.json** - Inventory of all processed files with metadata

## Usage

1. Place evidence files in the `raw/` directory
2. Run the processing script:
   ```bash
   python3 scripts/hash_evidence.py
   ```
3. The script will:
   - Calculate SHA-256 hash for each file
   - Move files to `hashed/` directory with hash-based filenames
   - Update `manifest.json` with file metadata

## Manifest Structure

The manifest.json file contains:
- List of all processed files with:
  - Original filename
  - Hashed filename (SHA-256 hash + extension)
  - SHA-256 hash value
  - File size in bytes
  - Processing timestamp
  - File path
- Metadata with creation and last updated timestamps

## Security

This system ensures:
- File integrity verification via SHA-256 hashes
- Deduplication (same file content produces same hash)
- Audit trail of all processed evidence files
