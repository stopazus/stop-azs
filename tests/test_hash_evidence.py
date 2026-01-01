#!/usr/bin/env python3
"""
Unit tests for the hash_evidence.py script.
"""

import hashlib
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
import sys

# Add the scripts directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

# Import functions from hash_evidence
from hash_evidence import calculate_sha256, load_manifest, save_manifest


class TestHashEvidence(unittest.TestCase):
    """Test cases for hash_evidence.py functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.txt")
        with open(self.test_file, 'w') as f:
            f.write("Test content for hashing")
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_calculate_sha256(self):
        """Test SHA-256 hash calculation."""
        expected_hash = hashlib.sha256(b"Test content for hashing").hexdigest()
        actual_hash = calculate_sha256(self.test_file)
        self.assertEqual(actual_hash, expected_hash)
    
    def test_load_manifest_new(self):
        """Test loading a new manifest that doesn't exist."""
        manifest_path = os.path.join(self.test_dir, "manifest.json")
        manifest = load_manifest(manifest_path)
        
        self.assertIn("files", manifest)
        self.assertIn("metadata", manifest)
        self.assertEqual(manifest["files"], [])
        self.assertIn("created", manifest["metadata"])
    
    def test_load_manifest_existing(self):
        """Test loading an existing manifest."""
        manifest_path = os.path.join(self.test_dir, "manifest.json")
        test_data = {
            "files": [{"test": "data"}],
            "metadata": {"created": "2025-01-01T00:00:00"}
        }
        
        with open(manifest_path, 'w') as f:
            json.dump(test_data, f)
        
        manifest = load_manifest(manifest_path)
        self.assertEqual(manifest["files"], [{"test": "data"}])
    
    def test_save_manifest(self):
        """Test saving manifest to file."""
        manifest_path = os.path.join(self.test_dir, "manifest.json")
        test_manifest = {
            "files": [{"filename": "test.txt"}],
            "metadata": {"created": "2025-01-01T00:00:00"}
        }
        
        save_manifest(manifest_path, test_manifest)
        
        self.assertTrue(os.path.exists(manifest_path))
        
        with open(manifest_path, 'r') as f:
            saved = json.load(f)
        
        self.assertIn("last_updated", saved["metadata"])
        self.assertEqual(saved["files"], [{"filename": "test.txt"}])


if __name__ == '__main__':
    unittest.main()
