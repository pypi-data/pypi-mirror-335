# Revised Test Plan: Function Detection and Change Analysis

This document outlines an updated testing strategy for Phase 2 of DiffScope, aligning with the current codebase structure and implementation status.

## Current Test Coverage
- ✅ Basic model tests implemented
- ⚠️ Partial function parser tests exist
- ⚠️ Diff utilities tests need fixes
- ❌ Function detector tests pending
- ❌ Integration tests pending

## Test Structure

```
tests/
├── unit/
│   ├── parsers/
│   │   ├── test_tree_sitter.py
│   │   └── test_function_parser.py
│   ├── utils/
│   │   └── test_diff_utils.py
│   ├── core/
│   │   └── test_function_detector.py
│   └── test_models.py
├── integration/
│   └── test_commit_analysis.py
└── samples/
    ├── python/
    ├── javascript/
    └── diff_samples/
```

## Prioritized Test Areas

### 1. Function Parsing (High Priority)
| Test Focus | Description |
|------------|-------------|
| Basic parsing | Test parsing of basic functions in supported languages |
| Edge cases | Test anonymous functions, nested functions, decorators |
| Line accuracy | Verify correct start/end line identification |
| Multiple languages | Test consistent behavior across all supported languages |
| CLI usage | Test command-line interface for direct testing |

### 2. Diff Analysis (High Priority)
| Test Focus | Description |
|------------|-------------|
| Basic diffs | Test parsing simple additions and deletions |
| Complex diffs | Test multi-hunk diffs and complex changes |
| Line mapping | Test mapping between original and new line numbers |
| Special cases | Test renamed files, new files, deleted files |
| Function diffs | Test extracting function-specific diffs from file diffs |

### 3. Function Change Detection (Medium Priority)
| Test Focus | Description |
|------------|-------------|
| Change detection | Test identification of changed functions |
| Change classification | Test classification into signature/body/docstring changes |
| Renamed functions | Test detection of renamed functions |
| Special cases | Test handling of moves between files, nested changes |
| API consistency | Test consistent use of model classes |

### 4. Integration Tests (Medium Priority)
| Test Focus | Description |
|------------|-------------|
| Basic workflow | Test end-to-end function from commit URL to results |
| GitHub integration | Test with actual GitHub repositories |
| Multiple languages | Test repositories with mixed language content |
| Error handling | Test graceful handling of API errors, rate limits |
| Performance | Test with large repositories and complex commits |

## Test Data Requirements

### Function Samples
- Create more comprehensive sample files for each language:
  - Python: Functions, methods, decorated functions, nested functions
  - JavaScript: Functions, arrow functions, methods, class definitions
  - Additional languages: Basic function patterns for each supported language

### Diff Samples
- Simple: Single-function changes with clear boundaries
- Complex: Multi-function changes spanning multiple hunks
- Edge cases: 
  - Renamed files with function changes
  - Changes that span function boundaries
  - Functions with unusual formatting or structure

## Testing Approach

### Unit Testing Focus
1. **Fix existing tests**:
   - Address failing tests in test_diff_utils.py
   - Ensure test_function_parser.py handles all edge cases
   - Make test_models.py align with actual model structure

2. **Add new component tests**:
   - Develop tests for each new module as it's implemented
   - Focus on both happy path and error cases
   - Test with both simple and complex inputs

3. **Use test-driven development**:
   - Write tests before implementing new features
   - Use tests to define expected behavior
   - Refactor with confidence using test suite

### Integration Testing
1. **Basic integration**:
   - Test function detection with actual diffs
   - Validate change detection with known changes
   - Verify model consistency across components

2. **End-to-end workflow**:
   - Test the complete analysis pipeline
   - Validate with real GitHub commits
   - Test with a variety of repository types

## Testing Tools and Approaches
- **pytest fixtures**: Create reusable test data and context
- **Parameterized tests**: Test multiple scenarios efficiently
- **Mock objects**: Isolate components during testing
- **CLI helpers**: Allow direct testing of parser and detectors
- **Sample repositories**: Create known test cases for full integration testing 