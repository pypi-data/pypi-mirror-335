#!/usr/bin/env python
"""
DiffScope CLI - Command-line interface for analyzing Git commits.
"""

import argparse
import json
import sys
from typing import Dict, Any, Optional

from . import analyze_commit, __version__
from .models import CommitAnalysisResult

def result_to_dict(result: CommitAnalysisResult) -> Dict[str, Any]:
    """Convert analysis result to a dictionary for JSON output."""
    return {
        "repository": result.repository,
        "commit_sha": result.commit_sha,
        "commit_message": result.commit_message,
        "commit_author": result.commit_author,
        "commit_date": result.commit_date.isoformat() if result.commit_date else None,
        "files": [
            {
                "filename": file.filename,
                "status": file.status,
                "additions": file.additions,
                "deletions": file.deletions,
                "changes": file.changes,
            }
            for file in result.modified_files
        ],
        "functions": [
            {
                "name": func.name,
                "file": func.file,
                "change_type": func.change_type.value,
                "old_start_line": func.old_start_line,
                "old_end_line": func.old_end_line,
                "new_start_line": func.new_start_line,
                "new_end_line": func.new_end_line,
            }
            for func in result.modified_functions
        ],
    }

def display_result(result: CommitAnalysisResult, output_format: str = "text") -> None:
    """Display analysis results in the specified format."""
    if output_format == "json":
        print(json.dumps(result_to_dict(result), indent=2))
        return

    # Default to text format
    print(f"Repository: {result.repository}")
    print(f"Commit: {result.commit_sha}")
    print(f"Author: {result.commit_author}")
    print(f"Date: {result.commit_date}")
    print(f"Message: {result.commit_message}")
    print("\nModified Files:")
    for file in result.modified_files:
        print(f"  {file.filename} ({file.status}): +{file.additions} -{file.deletions}")
    
    print("\nModified Functions:")
    for func in result.modified_functions:
        print(f"  {func.file}:{func.name} ({func.change_type.value})")
        print(f"    Lines: {func.old_start_line}-{func.old_end_line} → {func.new_start_line}-{func.new_end_line}")

def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Analyze Git commits at the function level",
        prog="diffscope"
    )
    
    parser.add_argument(
        "commit_url",
        help="URL to a GitHub commit (e.g., https://github.com/owner/repo/commit/sha)"
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"DiffScope {__version__}"
    )
    
    args = parser.parse_args()
    
    try:
        result = analyze_commit(args.commit_url)
        display_result(result, args.format)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 