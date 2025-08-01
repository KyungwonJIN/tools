"""
File management utilities
"""

from .file_ops import move_files
from .rename_utils import batch_rename, add_prefix, add_suffix
from .file_utils import copy_files_by_pattern, find_duplicate_files

__all__ = [
    'move_files',
    'batch_rename',
    'add_prefix',
    'add_suffix',
    'copy_files_by_pattern',
    'find_duplicate_files',
]