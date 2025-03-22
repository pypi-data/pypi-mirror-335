# DiffScope Implementation Details

DiffScope implements a sophisticated approach to analyzing Git commits at the function level. This document provides a detailed overview of the implementation architecture and data flow.

## Project Structure

```
src/diffscope/
├── parsers/          # Function parsing using tree-sitter
├── core/             # Core analysis functionality
├── utils/            # Utility functions and tools
├── models.py         # Data models
└── __init__.py       # Main API

tests/
├── unit/             # Unit tests
├── integration/      # Integration tests
└── samples/          # Test data
```

## Architecture Overview

DiffScope follows a modular architecture with clear separation of concerns:

- **Core Analysis Pipeline**: Two-phase approach for efficient analysis
  - Phase 1: File-level analysis via GitHub API
  - Phase 2: Function-level analysis with tree-sitter parsing

- **Data Models**: Three primary data structures
  - `CommitAnalysisResult`: Container for all analysis data
  - `ModifiedFile`: Represents file-level changes
  - `ModifiedFunction`: Represents function-level changes

- **Language Support**: Tree-sitter integration for accurate parsing
  - Language-specific queries for function detection
  - Support for Python, JavaScript, TypeScript, Java, C/C++, Go

## Data Flow

The analysis follows a clear pipeline:

1. **Input Processing**
   - Parse GitHub URL to extract repository and commit information
   - Authenticate with GitHub API using provided token

2. **File-Level Analysis** (`git_analyzer.py`)
   - Fetch commit metadata and file changes from GitHub API
   - Identify modified, added, deleted, and renamed files
   - Perform language detection based on file extensions

3. **Function-Level Analysis** (`commit_analyzer.py`)
   - For each file, retrieve content before and after changes
   - Filter files based on language support and binary detection
   - Process files differently based on their status (added/modified/deleted)

4. **Function Detection** (`function_detector.py` & `function_parser.py`)
   - Parse code using tree-sitter with language-specific queries
   - Extract function metadata (name, position, content) 
   - Compare functions between file versions to detect changes

5. **Diff Analysis** (`diff_utils.py`)
   - Parse unified diff format to extract change information
   - Map line numbers between original and new file versions
   - Extract function-specific diffs for detailed change analysis

6. **Change Classification**
   - Identify function change types:
     - Added, deleted, renamed functions
     - Signature, body, and docstring changes
   - Detect renamed functions using similarity metrics

7. **Result Generation**
   - Compile comprehensive `CommitAnalysisResult` with all analysis data
   - Include both file and function-level changes

## Key Algorithms

1. **Function Change Detection**:
   - Extract functions from both old and new versions
   - Match functions by name and location
   - Compare function content to classify changes
   - Use diff analysis to identify specific changes

2. **Renamed Function Detection**:
   - Identify deleted and added functions across files
   - Compute similarity scores between function pairs
   - Match functions with high similarity scores
   - Apply heuristics to confirm renames vs. new implementations

3. **Diff Analysis and Line Mapping**:
   - Parse GitHub patch format into structured hunks
   - Map line numbers between original and new files
   - Associate diff hunks with specific functions
   - Handle edge cases like overlapping functions

## Error Handling and Robustness

DiffScope implements comprehensive error handling:

- Graceful degradation when GitHub API rate limits are reached
- Robust handling of malformed patches and unexpected code structures
- Skip analysis for unsupported languages and binary files
- Detailed logging for diagnosing issues

## Performance Optimizations

- Tree-sitter for efficient code parsing
- Two-phase analysis to avoid unnecessary processing
- Targeted function analysis based on diff information
- Progressive refinement from file-level to function-level details 