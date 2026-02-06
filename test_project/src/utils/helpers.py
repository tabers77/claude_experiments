"""
Utility functions for the minimal API.
"""
import uuid
from datetime import datetime, timezone


def generate_id() -> str:
    """Generate a unique identifier."""
    return str(uuid.uuid4())[:8]


def format_timestamp() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def validate_name(name: str) -> bool:
    """Validate that a name is not empty and not too long."""
    return bool(name) and len(name) <= 100
