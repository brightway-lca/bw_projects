"""Fixtures for bw_projects"""
import os


def check_dir(directory: str) -> bool:
    """Returns ``True`` if given path is a directory and writeable,
    ``False`` otherwise."""
    return os.path.isdir(directory) and os.access(directory, os.W_OK)
