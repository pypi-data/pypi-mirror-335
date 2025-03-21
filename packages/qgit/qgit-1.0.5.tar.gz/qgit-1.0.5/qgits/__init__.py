"""QGits - Quick Git operations automation tool.

This package provides automation and convenience functions for common Git operations.
"""

__version__ = "1.0.5"

"""QGit package initialization."""

from .qgit import main
from .cli import main as cli_main

__all__ = ['main', 'cli_main']
