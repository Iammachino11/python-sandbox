# Contributing to FLAC to MP3 Converter

First off, thank you for considering contributing to this project! It's people like you that make this tool better for everyone.

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please be respectful and constructive in all interactions.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (sample FLAC files if possible)
- **Describe the behavior you observed** and what you expected
- **Include error messages and logs**
- **Specify your environment** (OS, Python version, dependency versions)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **List any alternatives you've considered**

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write or update tests as needed
5. Ensure all tests pass
6. Update documentation if needed
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## Development Setup

1. **Clone your fork:**
   ```bash
   git clone https://github.com/yourusername/flac-to-mp3-converter.git
   cd flac-to-mp3-converter
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Install FFmpeg** (if not already installed):
   - macOS: `brew install ffmpeg`
   - Ubuntu/Debian: `sudo apt-get install ffmpeg`
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=flac_to_mp3_converter --cov-report=html

# Run specific test file
pytest tests/test_converter.py -v
```

### Code Formatting

We use `black` for code formatting:

```bash
# Format all Python files
black flac_to_mp3_converter.py tests/

# Check without making changes
black --check flac_to_mp3_converter.py
```

### Linting

```bash
# Run pylint
pylint flac_to_mp3_converter.py

# Run flake8
flake8 flac_to_mp3_converter.py --max-line-length=88

# Type checking with mypy
mypy flac_to_mp3_converter.py
```

### Testing Your Changes

Before submitting a PR, ensure:

1. All tests pass
2. Code is formatted with black
3. No linting errors
4. Test coverage hasn't decreased
5. Documentation is updated

```bash
# Quick validation
black flac_to_mp3_converter.py && \
pylint flac_to_mp3_converter.py && \
pytest tests/ -v
```

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use meaningful variable and function names
- Maximum line length: 88 characters (black default)
- Use type hints where appropriate
- Write docstrings for all functions and classes

### Example Code Style

```python
def convert_file(
    self,
    flac_path: Path,
    output_dir: Path
) -> Tuple[bool, str]:
    """
    Convert a single FLAC file to MP3.
    
    Args:
        flac_path: Path to the FLAC file
        output_dir: Output directory for the MP3 file
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Implementation here
    pass
```

### Documentation Style

- Use Google-style docstrings
- Include type hints in function signatures
- Provide examples in docstrings where helpful
- Keep README.md up to date

## Commit Messages

Write clear and descriptive commit messages:

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters
- Reference issues and pull requests liberally

Examples:
```
Add support for variable bitrate encoding

- Implement VBR quality settings
- Update documentation with VBR examples
- Add tests for VBR conversion

Fixes #123
```

## Project Structure

```
flac-to-mp3-converter/
├── flac_to_mp3_converter.py  # Main script
├── tests/                     # Test files
│   └── test_converter.py
├── docs/                      # Documentation (if applicable)
├── requirements.txt           # Production dependencies
├── requirements-dev.txt       # Development dependencies
├── setup.py                   # Package setup
├── README.md                  # Main documentation
├── CONTRIBUTING.md            # This file
├── LICENSE                    # MIT License
└── .gitignore                 # Git ignore rules
```

## Areas for Contribution

We especially welcome contributions in these areas:

- **Performance improvements** (parallel processing, optimization)
- **New features** (additional formats, GUI, web interface)
- **Better error handling** and user feedback
- **Documentation improvements** (examples, tutorials)
- **Test coverage** (more unit tests, integration tests)
- **Cross-platform compatibility** fixes
- **Internationalization** (i18n support)

## Questions?

Feel free to:
- Open an issue for discussion
- Reach out to maintainers
- Ask questions in pull requests

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Git commit history

Thank you for contributing! 🎵