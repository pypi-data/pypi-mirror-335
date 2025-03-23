# Phase 1 API Design - Python Library Approach

This document outlines the minimal API design for Phase 1 of DiffScope as a Python library, focusing solely on GitHub API integration for commit analysis.

## 1. GitHub API Client (`src/utils/github_api.py`)

```python
def parse_github_url(github_url: str) -> Tuple[str, str, str]:
    """
    Parse a GitHub URL to extract owner, repo, and commit SHA.
    
    Args:
        github_url: URL to a GitHub commit (e.g., https://github.com/owner/repo/commit/sha)
        
    Returns:
        Tuple of (owner, repo_name, commit_sha)
    """
    pass

def get_commit_data(owner: str, repo: str, commit_sha: str) -> Dict:
    """
    Get commit data from GitHub API.
    
    Args:
        owner: Repository owner
        repo: Repository name
        commit_sha: Commit SHA
        
    Returns:
        Dictionary containing commit data
    """
    pass

def get_commit_files(owner: str, repo: str, commit_sha: str) -> List[Dict]:
    """
    Get list of files changed in a commit from GitHub API.
    
    Args:
        owner: Repository owner
        repo: Repository name
        commit_sha: Commit SHA
        
    Returns:
        List of file data dictionaries
    """
    pass

def get_file_content(owner: str, repo: str, file_path: str, ref: str) -> str:
    """
    Get content of a file at a specific commit from GitHub API.
    
    Args:
        owner: Repository owner
        repo: Repository name
        file_path: Path to file in the repository
        ref: Commit SHA or branch name
        
    Returns:
        Content of the file as string
    """
    pass
```

## 2. Git Analyzer Module (`src/core/git_analyzer.py`)

```python
def analyze_github_commit(commit_url: str) -> CommitAnalysisResult:
    """
    Analyze a GitHub commit and extract file-level changes.
    
    Args:
        commit_url: URL to a GitHub commit
        
    Returns:
        CommitAnalysisResult with file-level changes
    """
    pass

def convert_github_files_to_modified_files(github_files: List[Dict]) -> List[ModifiedFile]:
    """
    Convert GitHub API file data to ModifiedFile objects.
    
    Args:
        github_files: List of file data from GitHub API
        
    Returns:
        List of ModifiedFile objects
    """
    pass

def detect_file_language(file_path: str) -> Optional[str]:
    """
    Detect programming language of a file based on extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Language name or None if unknown
    """
    pass
```

## 3. Main Library API (`src/__init__.py`)

```python
from .core.git_analyzer import analyze_github_commit
from .models import ModifiedFile, ModifiedFunction, CommitAnalysisResult

__all__ = ['analyze_commit', 'ModifiedFile', 'ModifiedFunction', 'CommitAnalysisResult']

def analyze_commit(commit_url: str) -> CommitAnalysisResult:
    """
    Analyze a Git commit and extract file-level changes.
    This is the main entry point for the library.
    
    Args:
        commit_url: URL to a Git commit (currently only GitHub is supported)
        
    Returns:
        CommitAnalysisResult object containing file and function level changes
    
    Example:
        >>> from diffscope import analyze_commit
        >>> result = analyze_commit("https://github.com/owner/repo/commit/abc123")
        >>> for file in result.modified_files:
        ...     print(f"File: {file.filename}, Changes: {file.changes}")
    """
    # For now, we only support GitHub commits
    return analyze_github_commit(commit_url)
```

## Implementation Notes

1. **Library-First Design**: Focus on providing a clean, importable API
2. **GitHub API Only**: Initially, only support GitHub URLs, with a plan to expand later
3. **Public Repositories**: Only public repositories supported initially
4. **Error Handling**: Basic validation and clear error messages
5. **Extensibility**: Design to allow adding support for other Git platforms later

This minimal approach focuses on building a usable Python library that can be imported and used in other projects. The design is simple but allows for future expansion.

## Example Usage

```python
# Example of how the library would be used
from diffscope import analyze_commit

# Analyze a commit
result = analyze_commit("https://github.com/owner/repo/commit/abc123")

# Access file-level changes
print(f"Commit: {result.commit_sha}")
print(f"Author: {result.commit_author}")
print(f"Message: {result.commit_message}")

# Display file changes
for file in result.modified_files:
    print(f"File: {file.filename}")
    print(f"Status: {file.status}")
    print(f"Changes: +{file.additions} -{file.deletions}")
    print(f"Language: {file.language}")
    
# Later phases will include function-level changes
# for func in result.modified_functions:
#     print(f"Function: {func.function_name} in {func.file_path}")
#     print(f"Change type: {func.change_type}")
#     print(f"Diff:\n{func.diff}")
``` 