# Phase 2 Development Plan: Function Detection and Change Analysis

## Overview

Phase 2 combines two critical aspects of the DiffScope project: function boundary detection and function-level change analysis. This combined approach provides a more cohesive implementation for identifying how functions change between different versions of code.

## Goals

- Implement Tree-sitter integration for code parsing using tree-sitter-language-pack
- Develop function boundary detection algorithms for multiple languages
- Map file changes to function boundaries
- Analyze function-level changes with detailed metadata
- Generate function-specific diffs and change classifications

## Architecture

```
┌────────────────┐    ┌────────────────┐    ┌────────────────┐    ┌────────────────┐
│                │    │                │    │                │    │                │
│  Tree-sitter   │───>│  Function      │───>│  Change        │───>│  Function      │
│  Integration   │    │  Extraction    │    │  Analysis      │    │  Change Output │
│                │    │                │    │                │    │                │
└────────────────┘    └────────────────┘    └────────────────┘    └────────────────┘
```

## Components

### 1. Tree-sitter Integration

- Integration with tree-sitter-language-pack library
- Language support management
- Tree-sitter query interface for function detection
- Leveraging existing language detection from Phase 1

### 2. Function Extraction

- Abstract syntax tree (AST) traversal
- Function boundary identification using tree-sitter queries
- Function metadata extraction (name, parameters, etc.)

### 3. Change Analysis

- Parse and interpret unified diff patches
- Determine precise changes within functions
- Analyze types of changes (signature, body, docstring)
- Detect renamed functions using similarity metrics

### 4. Function Change Output

- Generate function-specific diffs
- Classify changes (added, modified, removed, renamed)
- Create detailed change metadata (lines added/removed, change types)
- Populate the ModifiedFunction data model

## Step-by-Step Development Plan

### Step 1: Tree-sitter Integration (Week 1)
1. Set up tree-sitter-language-pack dependencies
2. Create utility functions for parser and language management
3. Implement language detection and validation
4. Create caching mechanisms for parsers
5. **Testing**: Verify parser initialization for supported languages

### Step 2: Basic Function Detection (Week 1-2)
1. Create language-specific query patterns for functions
2. Implement function boundary detection for Python
3. Extend to JavaScript function detection
4. Extract function metadata (name, parameters)
5. **Testing**: Verify correct function detection across different code samples

### Step 3: Diff Parsing and Processing (Week 2)
1. Implement unified diff parser
2. Create line mapping between diff and source code
3. Develop heuristics for matching changes to line numbers
4. **Testing**: Verify correct parsing of various diff formats and scenarios

### Step 4: Function Change Analysis (Week 3)
1. Implement function content extraction
2. Develop comparison logic between function versions
3. Create change classification system (signature/body/docstring changes)
4. Add metadata generation for changes
5. **Testing**: Verify correct change detection and classification

### Step 5: Renamed Function Detection (Week 3)
1. Implement similarity metrics for function comparison
2. Create detection algorithm for renamed functions
3. Build confidence scoring for rename detection
4. **Testing**: Verify correct identification of renamed vs added/removed functions

### Step 6: Function-Specific Diff Generation (Week 4)
1. Create function-specific diff extractor
2. Format diffs for readability and context
3. Handle special cases and edge conditions
4. **Testing**: Verify accurate function-specific diff extraction

### Step 7: Integration with Phase 1 (Week 4)
1. Connect to file-level change detection from Phase 1
2. Integrate language detection
3. Create unified API for analyzing commits
4. **Testing**: Verify end-to-end functionality with sample repositories

## Comprehensive Test Plan

### Unit Tests

#### Tree-sitter Integration
- Test parser initialization for different languages
- Test language detection and validation
- Test error handling for unsupported languages

#### Function Detection
- Test Python function and method detection
- Test JavaScript function detection (all types)
- Test handling of nested functions
- Test anonymous functions and edge cases
- Test accuracy of function boundary determination

#### Diff Analysis
- Test unified diff parsing
- Test line number mapping
- Test change detection accuracy
- Test function-specific diff extraction

#### Change Classification
- Test accurate detection of signature changes
- Test accurate detection of body changes
- Test accurate detection of docstring changes
- Test detection of trivial vs. significant changes

#### Renamed Function Detection
- Test similarity algorithm with different thresholds
- Test detection of renamed vs. modified functions
- Test handling of edge cases (similar functions)

### Integration Tests

- Test end-to-end function change detection on sample repositories
- Test with multiple languages in the same repository
- Test with different types of commits (simple changes, refactors, renames)
- Test performance with large files and commits

### Performance Tests

- Benchmark parsing time for different file sizes
- Test memory consumption for large repositories
- Evaluate caching strategies effectiveness

## Technical Considerations

### Tree-sitter-language-pack Integration

The tree-sitter-language-pack library provides pre-built parsers for 100+ languages:

1. Install the library
   ```
   pip install tree-sitter-language-pack
   ```

2. Access parsers and languages
   ```python
   from tree_sitter_language_pack import get_language, get_parser
   
   # Get a language
   python_lang = get_language('python')
   
   # Get a parser
   python_parser = get_parser('python')
   ```

3. Parse code and query the syntax tree
   ```python
   parser = get_parser('python')
   tree = parser.parse(bytes(source_code, 'utf8'))
   
   # Query the tree for functions
   query = python_lang.query('(function_definition) @function')
   captures = query.captures(tree.root_node)
   ```

### Diff Analysis Techniques

1. Unified diff parsing to extract line-level changes
2. Mapping line changes to function boundaries
3. Using difflib for detailed content comparison
4. Heuristic-based classification of change types

### Language-Specific Challenges

Different languages have different function concepts that require custom queries:

- **Python**: Functions, methods, and nested functions (using `function_definition` nodes)
- **JavaScript**: Functions, arrow functions, methods, class methods
- **Handling Edge Cases**: Anonymous functions, lambdas, closures

### Performance Considerations

- Tree-sitter is designed for incremental parsing, which helps with performance
- For large files, consider parsing only changed parts
- Cache parsed trees when appropriate
- Optimize diff parsing for large changes

## Deliverables

By the end of Phase 2, we will deliver:

1. Tree-sitter integration with language-pack support
2. Function boundary detection for multiple languages (starting with Python and JavaScript)
3. Function-level change detection with detailed analysis
4. Renamed function detection capabilities
5. Function-specific diff generation
6. Integration with the Phase 1 components
7. Comprehensive unit and integration tests
8. Detailed documentation for all components

## Evaluation Criteria

The success of Phase 2 will be measured by:

1. Accuracy of function boundary detection
2. Precision of function change classification
3. Effectiveness of renamed function detection
4. Performance on large files and repositories
5. Robustness with edge cases
6. Integration with Phase 1 components
7. Test coverage and documentation quality 