# GitHub Copilot Instructions

This repository documents allegations and evidence of escrow fund diversion involving a City National Bank trust account. It includes Python utilities for validating SAR (Suspicious Activity Report) XML documents.

## Project Overview

- **Purpose**: Legal/investigative documentation and SAR XML validation
- **Primary Language**: Python 3.10 (as specified in CI/CD workflows)
- **Key Components**:
  - `analysis.md` - Detailed investigation documentation
  - `sar_parser/` - SAR XML validator utilities
  - `tests/` - Unit tests using Python's unittest framework

## Important Files to Reference

When working on issues, always review these key files for context:
- `analysis.md` - Core investigation documentation
- `sar_parser/validator.py` - Main validation logic
- `tests/test_validator.py` - Test cases and examples

## Code Style and Standards

### Python Code
- Follow PEP 8 style guidelines
- Use type hints (annotations) for all function parameters and return values
- Write clear docstrings following the existing format in `validator.py`
- Use dataclasses with `slots=True` for data structures
- Keep modules intentionally dependency-free where possible (like `validator.py`)

### Testing
- Use Python's built-in `unittest` framework (not pytest)
- Test files should be named `test_*.py` and placed in the `tests/` directory
- All new functionality must include corresponding unit tests
- Tests should validate both success and failure cases

### Documentation
- Maintain detailed docstrings explaining the purpose and behavior
- Update `analysis.md` only when adding substantive investigative content
- Use clear, professional language appropriate for legal/investigative context

## Build and Test Commands

### Running Tests
```bash
# Run all tests with unittest (use 'python3' or 'python' depending on your environment)
python3 -m unittest discover -s tests -v

# Run a specific test file
python3 -m unittest tests.test_validator -v
```

**Note**: Use `python3` on systems where both Python 2 and 3 are installed, or `python` on systems with only Python 3.

### Code Quality
```bash
# Check for basic Python syntax errors (if flake8 is available)
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Check code style (if flake8 is available)
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

### Running the Validator
```python
from sar_parser import validate_file, validate_string

# Validate an XML file
result = validate_file("path/to/sar.xml")
if result.is_valid:
    print("Document is valid")
else:
    for error in result.errors:
        print(f"{error.location}: {error.message}")
```

## Project Structure

```
.
├── .github/              # GitHub configuration and workflows
│   ├── workflows/        # CI/CD workflows (Python, CodeQL, etc.)
│   └── copilot-instructions.md
├── analysis.md           # Primary investigation documentation
├── SECURITY.md           # Security policies
├── sar_parser/           # SAR XML validation utilities
│   ├── __init__.py
│   └── validator.py      # Core validation logic
├── tests/                # Unit tests
│   └── test_validator.py
├── docs/                 # Additional documentation
└── tools/                # Utility scripts
```

## Security Considerations

- **No Secrets**: Never commit credentials, API keys, or sensitive personal information
- **Data Privacy**: This repository documents a legal investigation - be mindful of privacy and confidentiality
- **Input Validation**: The SAR validator handles potentially malformed XML - always validate input thoroughly
- **Dependency Management**: Keep the validator.py module dependency-free to minimize attack surface

## Development Workflow

1. **Before Making Changes**:
   - Review `analysis.md` and relevant code to understand context
   - Run existing tests to ensure they pass: `python3 -m unittest discover -s tests -v`

2. **When Adding Features**:
   - Add type hints to all new functions
   - Write comprehensive unit tests
   - Update docstrings to explain the new functionality
   - Ensure code follows existing patterns in `validator.py`

3. **When Modifying Documentation**:
   - Maintain professional, factual tone appropriate for legal/investigative use
   - Preserve existing structure and formatting in `analysis.md`
   - Ensure changes are substantive and well-sourced

4. **Before Committing**:
   - Run all tests and ensure they pass
   - Verify no sensitive data is being committed
   - Check that only relevant files are staged (no `__pycache__`, etc.)

## Validation Logic Patterns

The SAR validator follows these patterns:
- Returns `ValidationResult` objects containing a list of `ValidationError` instances (in the `errors` field)
- Each error includes: message, location (XPath-like), and severity
- Checks for: malformed XML, missing required blocks, placeholder values, incorrect data formats
- Uses defensive programming with try/except for XML parsing
- Provides human-readable error messages for end users

## Contact

For questions or issues, contact the repository owner as noted in the project documentation.

## CI/CD

The repository uses GitHub Actions for:
- Python package testing (Python 3.10)
- Code quality checks with flake8
- CodeQL security scanning
- Static analysis with Codacy

Ensure all changes pass CI checks before merging.
