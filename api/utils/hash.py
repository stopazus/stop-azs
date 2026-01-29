"""Hash computation utilities for evidence logging."""

import hashlib


def compute_content_hash(content: str) -> str:
    """
    Compute SHA256 hash of content for evidence logging.
    
    Args:
        content: The content to hash (typically SAR XML)
        
    Returns:
        Hex-encoded SHA256 hash
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()
