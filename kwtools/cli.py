"""
Command Line Interface for KW tools
"""

import click
from .file_management.file_ops import cli as file_ops_cli
from .file_management.rename_utils import cli as rename_cli
from .file_management.file_utils import cli as file_utils_cli
from .data_management.label_analyzer import cli as label_cli
from .data_management.dataset_utils import cli as dataset_cli
from .data_management.image_stats import cli as image_cli
from .data_management.label_modifier import cli as label_mod_cli
from .data_management.label_cleaner import cli as label_clean_cli

@click.group()
def main():
    """KW's utility tools for file and data management"""
    pass

# File management commands
main.add_command(file_ops_cli, name='file')
main.add_command(rename_cli, name='rename')
main.add_command(file_utils_cli, name='utils')

# Data management commands
main.add_command(label_cli, name='label')
main.add_command(dataset_cli, name='dataset')
main.add_command(image_cli, name='image')
main.add_command(label_mod_cli, name='modify')
main.add_command(label_clean_cli, name='clean')

if __name__ == '__main__':
    main()