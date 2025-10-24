#!/usr/bin/env python3
"""
fill_hash_manifest.py
Auto-fills SHA-256 checksums and UTC timestamps into the Excel manifest (SHA256_Manifest_7065f609.xlsx).
Place this script and all listed files in the same folder, then run:
    python fill_hash_manifest.py
"""

import hashlib
import os
import datetime
import openpyxl

manifest = "SHA256_Manifest_7065f609.xlsx"

if not os.path.exists(manifest):
    print(f"❌ Manifest not found: {manifest}")
    exit(1)

wb = openpyxl.load_workbook(manifest)
ws = wb.active

updated_rows = 0

for row in range(2, ws.max_row + 1):
    file_name = ws[f'A{row}'].value
    if not file_name or not os.path.exists(file_name):
        continue

    with open(file_name, 'rb') as f:
        sha256_hash = hashlib.sha256(f.read()).hexdigest()

    ws[f'C{row}'] = sha256_hash
    ws[f'D{row}'] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    updated_rows += 1

wb.save(manifest)
print(f"✅ Updated {updated_rows} record(s) with SHA-256 and timestamp in {manifest}")
