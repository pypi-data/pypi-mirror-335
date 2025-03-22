# DiffScope API Reference

This document provides a detailed reference for DiffScope's Python API.

## Main Functions

### analyze_commit

```python
from diffscope import analyze_commit

result = analyze_commit("https://github.com/owner/repo/commit/sha")
```

Analyzes a Git commit and extracts both file-level and function-level changes.

**Parameters:**
- `commit_url` (str): URL to a GitHub commit

**Returns:**
- `CommitAnalysisResult` object containing file and function level changes

## Data Models

### CommitAnalysisResult

```python
class CommitAnalysisResult:
    """Contains the results of analyzing a git commit."""
```

**Attributes:**
- `owner` (str): Repository owner name
- `repo` (str): Repository name
- `commit_sha` (str): Full SHA of the analyzed commit
- `repository_url` (str): URL to the repository
- `commit_author` (str, optional): Author of the commit
- `commit_date` (str, optional): Date of the commit
- `commit_message` (str, optional): Full commit message
- `modified_files` (List[ModifiedFile]): List of files changed in the commit
- `modified_functions` (List[ModifiedFunction]): List of functions changed in the commit

### ModifiedFile

```python
class ModifiedFile:
    """Information about a modified file in a commit."""
```

**Attributes:**
- `filename` (str): Path to the file
- `status` (str): Status of the file - 'added', 'modified', 'removed', or 'renamed'
- `additions` (int): Number of lines added
- `deletions` (int): Number of lines deleted
- `changes` (int): Total number of changes (additions + deletions)
- `language` (str, optional): Programming language of the file (if detected)
- `patch` (str, optional): Unified diff patch for the file (if available)
- `previous_filename` (str, optional): Original path for renamed files

### ModifiedFunction

```python
class ModifiedFunction:
    """Information about a modified function in a commit."""
```

**Attributes:**
- `name` (str): Function name
- `file` (str): File containing the function
- `type` (str): Type of the function ('function', 'method', etc.)
- `change_type` (FunctionChangeType): Type of change
- `original_start` (int, optional): Start line in the old version
- `original_end` (int, optional): End line in the old version
- `new_start` (int, optional): Start line in the new version
- `new_end` (int, optional): End line in the new version
- `changes` (int): Number of lines changed
- `diff` (str, optional): Function-specific diff
- `original_name` (str, optional): Previous name for renamed functions
- `original_content` (str, optional): Function content before changes
- `new_content` (str, optional): Function content after changes

### FunctionChangeType

```python
class FunctionChangeType(str, Enum):
    """Type of change to a function."""
```

**Values:**
- `ADDED` = "added": Function was added
- `MODIFIED` = "modified": Function was modified
- `REMOVED` = "removed": Function was deleted
- `RENAMED` = "renamed": Function was renamed

## Command Line Interface

The `diffscope` command can be used to analyze commits from the command line:

```bash
diffscope https://github.com/owner/repo/commit/sha
```

**Options:**
- `commit_url`: URL to a GitHub commit (required)
- `-f, --format`: Output format (text or json, default: text)
- `-v, --version`: Show version information

## GitHub Authentication

To use DiffScope effectively, you'll likely need to set a GitHub token to avoid API rate limits:

```bash
export GITHUB_TOKEN=your_token_here  # Linux/Mac
$env:GITHUB_TOKEN="your_token_here"  # Windows PowerShell
set GITHUB_TOKEN=your_token_here     # Windows CMD
``` 