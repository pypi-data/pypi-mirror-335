#!/usr/bin/env python
"""
Simple DiffScope Example

This example demonstrates basic usage of DiffScope to analyze a GitHub commit
and extract both file-level and function-level changes.

Usage:
    python simple_analysis.py <github_commit_url>

Example:
    python simple_analysis.py https://github.com/pytorch/pytorch/commit/a1e9d1c9
"""

import argparse
import os
import sys
from typing import Optional

from diffscope import analyze_commit
from diffscope.models import FunctionChangeType

def main(commit_url: str) -> None:
    """Analyze a GitHub commit and print the results."""
    print(f"Analyzing commit: {commit_url}")
    print("This may take a few seconds...\n")
    
    # Check for GitHub token
    if not os.environ.get("GITHUB_TOKEN"):
        print("Warning: No GITHUB_TOKEN environment variable found.")
        print("You may encounter rate limiting issues with the GitHub API.")
        print("For better performance, set a GitHub token in your environment:\n")
        print("  export GITHUB_TOKEN=your_token_here\n")
    
    try:
        # Analyze the commit
        result = analyze_commit(commit_url)
        
        # Print commit information
        print(f"Repository: {result.repository}")
        print(f"Commit: {result.commit_sha}")
        print(f"Author: {result.commit_author}")
        print(f"Date: {result.commit_date}")
        print(f"Message: {result.commit_message}\n")
        
        # Print file-level statistics
        print("File-level Changes:")
        print(f"  Files modified: {len(result.modified_files)}")
        total_additions = sum(f.additions for f in result.modified_files)
        total_deletions = sum(f.deletions for f in result.modified_files)
        print(f"  Total lines added: {total_additions}")
        print(f"  Total lines deleted: {total_deletions}\n")
        
        # Print function-level statistics
        print("Function-level Changes:")
        function_changes = {}
        for change_type in FunctionChangeType:
            function_changes[change_type] = 0
        
        for func in result.modified_functions:
            function_changes[func.change_type] += 1
        
        print(f"  Total functions changed: {len(result.modified_functions)}")
        for change_type, count in function_changes.items():
            if count > 0:
                print(f"  {change_type.value}: {count}")
        
        # Print detailed function changes
        print("\nDetailed Function Changes:")
        for func in result.modified_functions:
            print(f"  {func.file}:{func.name}")
            print(f"    Change type: {func.change_type.value}")
            if func.old_start_line and func.old_end_line:
                print(f"    Old location: Lines {func.old_start_line}-{func.old_end_line}")
            if func.new_start_line and func.new_end_line:
                print(f"    New location: Lines {func.new_start_line}-{func.new_end_line}")
            print()
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple DiffScope example")
    parser.add_argument(
        "commit_url",
        nargs="?",
        default="https://github.com/pytorch/pytorch/commit/a1e9d1c9",
        help="URL to a GitHub commit"
    )
    args = parser.parse_args()
    
    main(args.commit_url) 