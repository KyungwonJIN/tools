# KW Tools

Utility tools for file and data management, especially focused on handling YOLO format labels and dataset management.

## Installation

```bash
git clone [your-github-repo-url]
cd tools
pip install -e .
```

## Features

### File Management
- File moving and copying with pattern matching
- Batch file renaming (with prefix/suffix support)
- Duplicate file detection

### Data Management
- YOLO label analysis
- Dataset splitting (train/val/test)
- Label class modification
- Label cleaning (confidence value removal)
- Image statistics analysis

## Usage

### Label Analysis
```bash
# Analyze YOLO format labels
kwtools label analyze /path/to/labels
kwtools label analyze /path/to/labels --names classes.txt --recursive
```

### Label Modification
```bash
# Modify label classes
kwtools modify /path/to/labels mapping.json --format yolo
```

### Label Cleaning
```bash
# Remove confidence values from labels
kwtools clean /path/to/labels --recursive
```

### File Operations
```bash
# Move files
kwtools file move "*.jpg" /target/directory --recursive

# Rename files
kwtools rename prefix /path/to/files prefix_ --recursive
```

## License

[Your chosen license]