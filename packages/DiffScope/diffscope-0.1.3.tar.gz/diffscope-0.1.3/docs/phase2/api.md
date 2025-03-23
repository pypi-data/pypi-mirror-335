# Revised API Design: Function Detection and Change Analysis

This document outlines the updated API design for Phase 2 of the DiffScope project, aligning with the current implementation of function boundary detection and function-level change analysis.

## Data Models

```python
from typing import List, Dict, Optional, Any
from enum import Enum
from dataclasses import dataclass


class FileChangeType(str, Enum):
    """Type of change to a file."""
    ADDED = "added"
    MODIFIED = "modified"
    REMOVED = "removed"
    RENAMED = "renamed"


class FunctionChangeType(str, Enum):
    """Type of change to a function."""
    ADDED = "added"
    DELETED = "deleted"
    RENAMED = "renamed"
    SIGNATURE_CHANGED = "signature_changed"
    BODY_CHANGED = "body_changed"
    DOCSTRING_CHANGED = "docstring_changed"


@dataclass
class ModifiedFile:
    """Information about a modified file in a commit."""
    filename: str                      # Path to the file
    status: str                        # 'added', 'modified', 'removed', 'renamed'
    additions: int                     # Number of added lines
    deletions: int                     # Number of deleted lines
    changes: int                       # Total number of changes
    language: Optional[str] = None     # Programming language
    patch: Optional[str] = None        # Unified diff patch
    previous_filename: Optional[str] = None  # For renamed files


@dataclass
class ModifiedFunction:
    """Information about a modified function in a commit."""
    name: str                          # Function name
    file: str                          # Path to the file
    type: str                          # 'function', 'method', etc.
    change_type: FunctionChangeType    # Type of change
    original_start: Optional[int] = None  # Start line in original file
    original_end: Optional[int] = None    # End line in original file
    new_start: Optional[int] = None       # Start line in new file
    new_end: Optional[int] = None         # End line in new file
    changes: int = 0                      # Number of changes
    diff: Optional[str] = None            # Function-specific diff
    original_name: Optional[str] = None   # For renamed functions


@dataclass
class CommitAnalysisResult:
    """Result of analyzing a commit."""
    commit_sha: str
    repository_url: str
    commit_author: Optional[str] = None
    commit_date: Optional[str] = None
    commit_message: Optional[str] = None
    modified_files: List[ModifiedFile] = None
    modified_functions: List[ModifiedFunction] = None
    
    def __post_init__(self):
        if self.modified_files is None:
            self.modified_files = []
        if self.modified_functions is None:
            self.modified_functions = []
```

## Tree-sitter Integration (`src/parsers/tree_sitter_utils.py`)

```python
from typing import Dict, List, Optional, Union, Any
import logging

def get_tree_sitter_parser(language: str) -> Any:
    """
    Get a tree-sitter parser for the specified language.
    
    Args:
        language: Language name (e.g. 'python', 'javascript')
        
    Returns:
        Tree-sitter parser
    
    Raises:
        ValueError: If language is not supported
    """
    # Implementation uses tree-sitter-language-pack to get a parser
    pass

def get_tree_sitter_language(language: str) -> Any:
    """
    Get a tree-sitter language for the specified language.
    
    Args:
        language: Language name (e.g. 'python', 'javascript')
        
    Returns:
        Tree-sitter language
    
    Raises:
        ValueError: If language is not supported
    """
    # Implementation uses tree-sitter-language-pack to get a language
    pass

def is_language_supported(language: str) -> bool:
    """
    Check if a language is supported by tree-sitter.
    
    Args:
        language: Language name
        
    Returns:
        True if language is supported, False otherwise
    """
    # Check if the language has a parser and function query patterns
    pass

def parse_code(content: str, language: str) -> Any:
    """
    Parse source code using tree-sitter.
    
    Args:
        content: Source code content
        language: Programming language
        
    Returns:
        Parsed syntax tree
        
    Raises:
        ValueError: If language is not supported
    """
    # Parse code and return the syntax tree
    pass

def get_supported_languages() -> List[str]:
    """
    Get a list of all supported languages.
    
    Returns:
        List of supported language names
    """
    # Return languages with defined function query patterns
    pass
```

## Function Parsing (`src/parsers/function_parser.py`)

```python
from typing import List, Dict, Optional, Any
from .tree_sitter_utils import get_tree_sitter_parser, get_tree_sitter_language, is_language_supported

# Define function queries for supported languages
FUNCTION_QUERIES = {
    "python": """
        (function_definition
          name: (identifier) @function_name
        ) @function
        
        (class_definition
          name: (identifier) @class_name
          body: (block (function_definition
            name: (identifier) @method_name
          ) @method)
        )
    """,
    "javascript": """
        (function_declaration
          name: (identifier) @function_name
        ) @function
        
        (method_definition
          name: (property_identifier) @method_name
        ) @method
        
        (arrow_function) @arrow_function
        
        (variable_declarator
          name: (identifier) @var_name
          value: (arrow_function) @arrow_function_var
        )
    """,
    # Additional languages...
}

def parse_functions(content: str, language: str) -> List[Dict]:
    """
    Parse source code to identify functions.
    
    Args:
        content: Source code content
        language: Programming language
        
    Returns:
        List of dictionaries containing function information:
        [
            {
                'name': str,            # Function name
                'start_line': int,      # Start line (1-indexed)
                'end_line': int,        # End line (1-indexed)
                'parameters': List[str], # Parameter names
                'node_type': str        # 'function', 'method', etc.
            },
            ...
        ]
    """
    # Implementation details - use tree-sitter to parse functions
    pass

def get_function_at_line(content: str, language: str, line_number: int) -> Optional[Dict]:
    """
    Find the function containing the specified line number.
    
    Args:
        content: Source code content
        language: Programming language
        line_number: Line number to check (1-indexed)
        
    Returns:
        Function information if found, None otherwise
    """
    # Implementation details - find function containing the line
    pass

def extract_function_content(content: str, function_info: Dict) -> Optional[str]:
    """
    Extract the content of a function from file content.
    
    Args:
        content: Content of the file
        function_info: Dictionary with function information from parse_functions
        
    Returns:
        String containing the function code
    """
    # Implementation details - extract the function content
    pass

def is_node_within(node: Any, parent: Any) -> bool:
    """
    Check if a node is within another node.
    
    Args:
        node: The node to check
        parent: The potential parent node
        
    Returns:
        True if node is within parent, False otherwise
    """
    # Implementation details
    pass

def is_nearby(name_node: Any, func_node: Any, max_lines: int = 3) -> bool:
    """
    Check if a name node is nearby a function node.
    
    Args:
        name_node: The name node
        func_node: The function node
        max_lines: Maximum number of lines between nodes
        
    Returns:
        True if name node is nearby function node, False otherwise
    """
    # Implementation details
    pass
```

## Diff Utilities (`src/utils/diff_utils.py`)

```python
from typing import Dict, List, Tuple, Optional, Set, NamedTuple
import re
import logging

class HunkHeader(NamedTuple):
    """Represents a hunk header in a diff."""
    original_start: int
    original_count: int
    new_start: int
    new_count: int

class FileDiff(NamedTuple):
    """Represents a diff for a single file."""
    old_file: str
    new_file: str
    hunks: List[Tuple[HunkHeader, List[str]]]
    original_changes: Dict[int, str]  # line_number -> content
    new_changes: Dict[int, str]  # line_number -> content
    is_new: bool = False
    is_deleted: bool = False
    is_binary: bool = False
    is_rename: bool = False

def parse_diff(diff_content: str) -> List[FileDiff]:
    """
    Parse a unified diff string and return a list of FileDiff objects.
    
    Args:
        diff_content: The content of the diff.
        
    Returns:
        A list of FileDiff objects, one for each file in the diff.
    """
    # Implementation details
    pass

def _parse_file_diff(lines: List[str], start_idx: int) -> Optional[FileDiff]:
    """
    Parse a single file diff starting at the given index.
    
    Args:
        lines: The lines of the diff.
        start_idx: The index of the start of the file diff.
        
    Returns:
        A FileDiff object if successful, None otherwise.
    """
    # Implementation details
    pass

def _parse_hunk(lines: List[str], start_idx: int) -> Optional[Tuple[HunkHeader, List[str], int]]:
    """
    Parse a single hunk from the diff.
    
    Args:
        lines: The lines of the diff.
        start_idx: The index of the hunk header line.
        
    Returns:
        A tuple of (hunk_header, hunk_lines, next_idx) if successful, 
        or None if the hunk could not be parsed.
    """
    # Implementation details
    pass

def get_changed_line_numbers(file_diff: FileDiff) -> Tuple[Set[int], Set[int]]:
    """
    Get the set of changed line numbers for a file diff.
    
    Args:
        file_diff: FileDiff object
        
    Returns:
        Tuple of (original changed lines, new changed lines)
    """
    # Implementation details
    pass

def get_hunk_at_line(file_diff: FileDiff, new_line: int) -> Optional[Tuple[HunkHeader, List[str]]]:
    """
    Find the hunk containing a specific line number in the new file.
    
    Args:
        file_diff: FileDiff object
        new_line: Line number in the new file
        
    Returns:
        Hunk tuple if found, None otherwise
    """
    # Implementation details
    pass

def map_original_to_new_line(file_diff: FileDiff, original_line: int) -> Optional[int]:
    """
    Map a line number from the original file to the new file.
    
    Args:
        file_diff: The file diff.
        original_line: Line number in the original file.
        
    Returns:
        The corresponding line number in the new file, or None if the line was deleted.
    """
    # Implementation details
    pass

def map_new_to_original_line(file_diff: FileDiff, new_line: int) -> Optional[int]:
    """
    Map a line number from the new file to the original file.
    
    Args:
        file_diff: FileDiff object
        new_line: Line number in the new file
        
    Returns:
        Corresponding line number in the original file, or None if unmappable
    """
    # Implementation details
    pass

def generate_line_map(file_diff: FileDiff) -> Dict[int, Optional[int]]:
    """
    Generate a complete mapping of line numbers from new to original.
    
    Args:
        file_diff: FileDiff object
        
    Returns:
        Dictionary mapping new line numbers to original line numbers (None for added lines)
    """
    # Implementation details
    pass

def extract_function_diff(file_diff: FileDiff, func_start: int, func_end: int) -> Optional[str]:
    """
    Extract a diff limited to a specific function range in the new file.
    
    Args:
        file_diff: The file diff.
        func_start: The function start line in the new file.
        func_end: The function end line in the new file.
        
    Returns:
        A string containing the diff limited to the function, or None if there are no changes.
    """
    # Implementation details
    pass
```

## Function Change Detection (`src/core/function_detector.py`)

```python
from typing import List, Dict, Optional, Tuple, Set
from ..parsers.function_parser import parse_functions, get_function_at_line, extract_function_content
from ..parsers.tree_sitter_utils import is_language_supported
from ..utils.diff_utils import parse_diff, extract_function_diff, FileDiff
from ..models import ModifiedFunction, FunctionChangeType
import difflib
import re

def extract_functions_from_content(file_content: str, language: str, file_path: str = None) -> List[Dict]:
    """
    Extract function information from file content.
    
    Args:
        file_content: Content of the file
        language: Programming language of the file
        file_path: Optional path to the file for reference
        
    Returns:
        List of function information dictionaries
    """
    # Implementation details
    pass

def analyze_function_changes(before_func: Dict, after_func: Dict, 
                          before_content: str, after_content: str,
                          patch: str) -> Dict:
    """
    Analyze what aspects of a function changed between versions.
    
    Args:
        before_func: Function information before changes
        after_func: Function information after changes
        before_content: File content before changes
        after_content: File content after changes
        patch: Unified diff of the file
        
    Returns:
        Dictionary with change information
    """
    # Implementation details
    pass

def create_modified_functions(before_content: Optional[str], after_content: Optional[str], 
                           language: str, file_path: str, patch: Optional[str] = None) -> List[ModifiedFunction]:
    """
    Identify functions that were modified between two versions of a file.
    
    Args:
        before_content: Content of the file before changes
        after_content: Content of the file after changes
        language: Programming language of the file
        file_path: Path to the file
        patch: Optional unified diff of the file
        
    Returns:
        List of ModifiedFunction objects
    """
    # Implementation details
    pass

def detect_renamed_functions(modified_functions: List[ModifiedFunction]) -> None:
    """
    Identify renamed functions by comparing added and removed functions.
    Modifies the provided list in-place to update change types.
    
    Args:
        modified_functions: List of ModifiedFunction objects
    """
    # Implementation details
    pass

def calculate_function_similarity(content1: str, content2: str) -> float:
    """
    Calculate similarity between two function contents.
    
    Args:
        content1: First function content
        content2: Second function content
        
    Returns:
        Similarity score between 0 and 1
    """
    # Implementation details
    pass
```

## Main API (`src/__init__.py`)

```python
from typing import List, Dict, Optional
from .core.git_analyzer import analyze_github_commit
from .core.function_detector import create_modified_functions
from .utils.github_api import parse_github_url, get_file_content_before_after
from .parsers.tree_sitter_utils import is_language_supported
from .models import CommitAnalysisResult

def analyze_commit(commit_url: str) -> CommitAnalysisResult:
    """
    Analyze a Git commit and extract file and function level changes.
    
    Args:
        commit_url: URL to a Git commit
        
    Returns:
        CommitAnalysisResult with file and function level changes
    """
    # Implement complete workflow:
    # 1. Get file-level changes from Phase 1
    # 2. Process each file for function-level changes
    # 3. Return combined results
    pass
```

## Example Usage

```python
from diffscope import analyze_commit

# Analyze a commit with function-level details
result = analyze_commit("https://github.com/owner/repo/commit/abc123")

# Access file-level changes
print(f"Files changed: {len(result.modified_files)}")
for file in result.modified_files:
    print(f"File: {file.filename}")
    print(f"Status: {file.status}")
    print(f"Changes: {file.additions} additions, {file.deletions} deletions")

# Access function-level changes
print(f"Functions changed: {len(result.modified_functions)}")
for func in result.modified_functions:
    print(f"Function: {func.name} in {func.file}")
    print(f"Change type: {func.change_type}")
    
    if func.change_type == FunctionChangeType.RENAMED:
        print(f"Renamed from: {func.original_name}")
    elif func.change_type in (FunctionChangeType.BODY_CHANGED, FunctionChangeType.SIGNATURE_CHANGED):
        print(f"Lines: {func.new_start}-{func.new_end}")
        print(f"Changes: {func.changes} lines modified")
    
    if func.diff:
        print(f"Diff:\n{func.diff}")
``` 