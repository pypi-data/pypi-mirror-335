# DiffScope Quick Start Guide

This guide will help you get started with DiffScope, a function-level git commit analysis tool.

## Installation

You can install DiffScope directly from PyPI:

```bash
pip install diffscope
```

For development purposes, you can install from the source:

```bash
git clone https://github.com/yourusername/DiffScope.git
cd DiffScope
pip install -e .
```

## Using the Command Line Interface

DiffScope provides a simple command-line interface for analyzing commits:

```bash
# Basic usage with default text output
diffscope https://github.com/owner/repo/commit/sha

# Output in JSON format
diffscope https://github.com/owner/repo/commit/sha --format json
```

### CLI Options

- `commit_url`: URL to a GitHub commit (required)
- `-f, --format`: Output format (text or json, default: text)
- `-v, --version`: Show version information

## Using the Python API

```python
from diffscope import analyze_commit

# Analyze a GitHub commit
result = analyze_commit("https://github.com/owner/repo/commit/sha")

# Access file-level changes
for file in result.modified_files:
    print(f"File: {file.filename}")
    print(f"Status: {file.status}")
    print(f"Changes: +{file.additions} -{file.deletions}")

# Access function-level changes
for function in result.modified_functions:
    print(f"Function: {function.name} in {function.file}")
    print(f"Change type: {function.change_type}")
    print(f"Old location: {function.old_start_line}-{function.old_end_line}")
    print(f"New location: {function.new_start_line}-{function.new_end_line}")
```

## GitHub Authentication

To avoid rate limits, set a GitHub token in your environment:

```bash
# Linux/Mac
export GITHUB_TOKEN=your_token_here

# Windows PowerShell
$env:GITHUB_TOKEN="your_token_here"

# Windows CMD
set GITHUB_TOKEN=your_token_here
```

## Example Use Cases

### 1. Code Review Helper

Identify which functions changed in a PR to focus code review efforts.

### 2. Documentation Generation

Automatically document which components were affected by a change.

### 3. Change Impact Analysis

Understand the scope of a change by seeing exactly which functions were modified.

### 4. Migration Planning

Analyze patterns of changes across multiple commits to plan code migrations.

## Next Steps

- Check out the [Examples](../examples/) directory for more detailed usage examples
- Read the [Full Documentation](https://diffscope.readthedocs.io) for API details
- Explore the [Contributing Guide](../CONTRIBUTING.md) to help improve DiffScope 