"""
KW's utility tools for file and data management
"""

from . import file_management
from . import data_management

# File management utilities
from .file_management import (
    move_files,
    batch_rename,
    add_prefix,
    add_suffix,
    copy_files_by_pattern,
    find_duplicate_files,
)

# Data management utilities
from .data_management import (
    analyze_labels,
    split_dataset,
    convert_yolo_to_coco,
    analyze_images,
)

__version__ = "0.1.0"

__all__ = [
    'move_files',
    'batch_rename',
    'add_prefix',
    'add_suffix',
    'copy_files_by_pattern',
    'find_duplicate_files',
    'analyze_labels',
    'split_dataset',
    'convert_yolo_to_coco',
    'analyze_images',
]