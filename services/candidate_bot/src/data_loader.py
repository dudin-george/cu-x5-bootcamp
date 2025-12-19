"""Load data from text files."""

import os
from functools import lru_cache
from pathlib import Path

# Data directory path
DATA_DIR = Path(__file__).parent / "data"


def read_lines(filename: str) -> list[str]:
    """Read lines from a file, stripping whitespace.
    
    Args:
        filename: File name in data directory.
        
    Returns:
        List of non-empty lines.
    """
    filepath = DATA_DIR / filename
    if not filepath.exists():
        return []
    
    with open(filepath, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


@lru_cache(maxsize=1)
def get_priorities() -> list[str]:
    """Get priority options."""
    return read_lines("priorities.txt")


@lru_cache(maxsize=1)
def get_courses() -> list[str]:
    """Get course options."""
    return read_lines("courses.txt")


@lru_cache(maxsize=1)
def get_sources() -> list[str]:
    """Get source options."""
    return read_lines("sources.txt")


@lru_cache(maxsize=1)
def get_universities() -> list[str]:
    """Get university options."""
    return read_lines("universities.txt")


# Pre-load data on import
PRIORITIES = get_priorities()
COURSES = get_courses()
SOURCES = get_sources()
UNIVERSITIES = get_universities()

