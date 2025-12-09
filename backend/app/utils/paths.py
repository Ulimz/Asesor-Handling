"""
Utility functions for common operations across the application.
"""
import os
from pathlib import Path


def get_data_dir() -> Path:
    """
    Get the data directory path, handling both Docker and local environments.
    
    Returns:
        Path: Path to the data directory
    """
    if os.path.exists("/app/data"):
        return Path("/app/data")
    else:
        # Local development - go up from app/utils to backend, then to data
        return Path(__file__).parent.parent.parent / "data"


def get_xml_dir() -> Path:
    """Get the XML files directory."""
    return get_data_dir() / "xml"


def get_xml_parsed_dir() -> Path:
    """Get the parsed XML files directory."""
    return get_data_dir() / "xml_parsed"
