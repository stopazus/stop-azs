"""Tests for utility functions."""

import pytest
from api.utils.hash import compute_content_hash


def test_compute_content_hash():
    """Test SHA256 hash computation."""
    content = "test content"
    hash1 = compute_content_hash(content)
    
    # Should be 64 characters (hex-encoded SHA256)
    assert len(hash1) == 64
    
    # Should be deterministic
    hash2 = compute_content_hash(content)
    assert hash1 == hash2


def test_compute_content_hash_different_content():
    """Test that different content produces different hashes."""
    hash1 = compute_content_hash("content1")
    hash2 = compute_content_hash("content2")
    
    assert hash1 != hash2


def test_compute_content_hash_unicode():
    """Test hash computation with unicode content."""
    content = "test content with unicode: 你好世界"
    hash_value = compute_content_hash(content)
    
    # Should handle unicode correctly
    assert len(hash_value) == 64
    
    # Should be deterministic
    hash_value2 = compute_content_hash(content)
    assert hash_value == hash_value2
