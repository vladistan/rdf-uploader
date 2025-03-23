"""Utility functions for the RDF uploader."""

import os
import re
from pathlib import Path


def get_env_value(key: str, default: str = "") -> str:
    """
    Get a value from environment variables.

    If the value is not found in environment variables, try to read it from .envrc file.
    If still not found, return the default value.

    Args:
        key: The environment variable key
        default: The default value to return if the key is not found

    Returns:
        The value from environment variables, .envrc, or the default
    """
    # First check environment variables
    value = os.environ.get(key)
    if value is not None:
        return value

    # Then check .envrc file
    envrc_path = Path.cwd() / ".envrc"
    if envrc_path.exists():
        content = envrc_path.read_text()
        pattern = rf'export\s+{key}=(["\']?)(.+?)(\1)(?:\s|$)'
        match = re.search(pattern, content)
        if match:
            return match.group(2)

    # Return default if not found
    return default
