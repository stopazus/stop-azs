#!/usr/bin/env python3
"""
Demonstration script for the Master Exhibit Index.

This script shows how to use the exhibit_index module to work with
the Master Exhibit Index data.
"""

import sys
from pathlib import Path

# Add parent directory to path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from exhibit_index import load_master_exhibit_index


def main():
    # Load the Master Exhibit Index
    print("Loading Master Exhibit Index...\n")
    mei = load_master_exhibit_index()
    
    # Display summary
    print("=" * 70)
    print("MASTER EXHIBIT INDEX SUMMARY")
    print("=" * 70)
    print(f"Total exhibits: {len(mei.exhibits)}")
    print(f"Filed exhibits: {len(mei.get_filed_exhibits())}")
    print()
    
    # List all exhibits
    print("=" * 70)
    print("ALL EXHIBITS")
    print("=" * 70)
    for exhibit in mei.exhibits:
        print(f"\nExhibit {exhibit.exhibit_id}: {exhibit.title}")
        print(f"  Status: {exhibit.status}")
        print(f"  Bates Range: {exhibit.bates_range}")
        
        if exhibit.file_name:
            print(f"  File: {exhibit.file_name}")
        
        if exhibit.sha256_hash:
            print(f"  SHA-256: {exhibit.sha256_hash}")
        
        if exhibit.prepared_by:
            print(f"  Prepared By: {exhibit.prepared_by}")
            
        if exhibit.prepared_date:
            print(f"  Prepared Date: {exhibit.prepared_date}")
        
        if exhibit.notes:
            print(f"  Notes: {exhibit.notes}")
    
    print()
    print("=" * 70)
    
    # Example: Get a specific exhibit
    print("\nExample: Retrieving Exhibit E-1...")
    exhibit_e1 = mei.get_exhibit_by_id("E-1")
    if exhibit_e1:
        print(f"Found: {exhibit_e1.title}")
        print(f"This exhibit has detailed metadata including:")
        print(f"  - File name: {exhibit_e1.file_name}")
        print(f"  - Cryptographic hash for integrity verification")
        print(f"  - Preparation metadata")
    
    print("\n" + "=" * 70)
    print("Done!")


if __name__ == "__main__":
    main()
