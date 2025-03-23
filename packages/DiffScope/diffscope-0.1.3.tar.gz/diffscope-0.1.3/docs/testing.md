# Testing DiffScope

DiffScope includes a comprehensive test suite with both unit tests and integration tests. This document provides instructions for running and extending these tests.

## Running Tests

### Unit Tests

Run the unit tests (no GitHub API calls):

```bash
python -m pytest tests/unit
```

### Integration Tests

Integration tests require the `--run-live-api` flag to enable tests that make real GitHub API calls:

```bash
# Run with a GitHub token to avoid rate limits
export GITHUB_TOKEN=your_token_here
python -m pytest tests/integration --run-live-api
```

You can also use the provided test helper:

```bash
# Run all tests including integration tests
python tests/run_tests.py --all --token=your_github_token_here
```

### Testing with Verbose Output

To see detailed test output including function changes:

```bash
python -m pytest tests/integration/test_commit_analysis.py -v -s --run-live-api
```

### Testing Specific Commits

You can test with specific commits by using the `--commit_file` option:

```bash
python -m pytest tests/integration --run-live-api --commit_file=tests/test-repo/commit_urls.txt
```

## Test Structure

- **Unit Tests** (`tests/unit/`): Test individual components without external dependencies
- **Integration Tests** (`tests/integration/`): Test end-to-end functionality with actual GitHub repos
- **Test Repo** (`tests/test-repo/`): Sample code in different languages for testing

## Adding Tests

When adding new features, please add corresponding tests:

### Unit Tests

For isolated functionality that doesn't require API calls:

```python
# Example: tests/unit/test_function_parser.py
def test_parse_python_function():
    parser = PythonFunctionParser()
    code = "def example(): return 42"
    functions = parser.parse(code)
    assert len(functions) == 1
    assert functions[0].name == "example"
```

### Integration Tests

For end-to-end testing with real GitHub commits:

```python
# Example: tests/integration/test_commit_analysis.py
@pytest.mark.require_api
def test_analyze_specific_commit():
    result = analyze_commit("https://github.com/owner/repo/commit/sha")
    assert result is not None
    assert len(result.modified_files) > 0
```

## Test Configuration

You can configure test behavior with environment variables:

- `GITHUB_TOKEN`: Authentication token for GitHub API
- `DIFFSCOPE_TEST_CACHE`: Set to "1" to cache API responses for faster testing 