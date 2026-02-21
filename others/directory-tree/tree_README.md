# Directory Tree Generator

A professional Python tool for generating visual directory tree structures with multiple output formats and extensive customization options.

## Features

- **Multiple Output Formats**: Text, Markdown, HTML, and JSON
- **Smart Filtering**: Ignore patterns, hidden files, and directories
- **Depth Control**: Limit tree depth for large directories
- **File Information**: Optional file sizes and permissions
- **Default Ignores**: Automatically skips common directories (node_modules, .git, etc.)
- **Beautiful Output**: Clean, professional tree visualization
- **Highly Configurable**: CLI arguments or interactive mode
- **Statistics**: Detailed counts of files, directories, and errors
- **Error Handling**: Gracefully handles permission errors and missing directories

## Installation

### Prerequisites

- Python 3.7 or higher

### Install

No external dependencies required! Uses only Python standard library.

```bash
# Clone or download the script
pip install -e .  # Optional: install as package
```

## Usage

### Basic Usage

```bash
# Interactive mode (prompts for all options)
python directory_tree_generator.py

# Command-line mode
python directory_tree_generator.py /path/to/directory output.txt

# Quick example
python directory_tree_generator.py ~/Projects project_tree.txt
```

### Output Formats

#### Text Format (Default)
```bash
python directory_tree_generator.py /path/to/dir tree.txt

# Output:
# my_project
# ├── src
# │   ├── main.py
# │   └── utils.py
# ├── tests
# │   └── test_main.py
# └── README.md
```

#### Markdown Format
```bash
python directory_tree_generator.py /path/to/dir tree.md --format markdown

# Output:
# # my_project
#
# - **src/**
#   - main.py
#   - utils.py
# - **tests/**
#   - test_main.py
# - README.md
```

#### HTML Format
```bash
python directory_tree_generator.py /path/to/dir tree.html --format html
```

Generates a styled HTML page with collapsible folders and syntax highlighting.

#### JSON Format
```bash
python directory_tree_generator.py /path/to/dir tree.json --format json

# Output:
# {
#   "name": "my_project",
#   "type": "directory",
#   "children": [
#     {
#       "name": "src",
#       "type": "directory",
#       "children": [...]
#     }
#   ]
# }
```

### Advanced Options

```bash
# Limit depth to 2 levels
python directory_tree_generator.py /path/to/dir tree.txt -d 2

# Show hidden files
python directory_tree_generator.py /path/to/dir tree.txt --show-hidden

# Show directories only
python directory_tree_generator.py /path/to/dir tree.txt --dirs-only

# Show file sizes
python directory_tree_generator.py /path/to/dir tree.txt --show-size

# Show file permissions (Unix)
python directory_tree_generator.py /path/to/dir tree.txt --show-permissions

# Ignore specific patterns
python directory_tree_generator.py /path/to/dir tree.txt \
    --ignore node_modules \
    --ignore "*.pyc" \
    --ignore __pycache__

# Combine multiple options
python directory_tree_generator.py ~/Projects tree.md \
    --format markdown \
    --max-depth 3 \
    --dirs-only \
    --show-hidden \
    --verbose
```

### Command-Line Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `directory` | - | Source directory | Interactive prompt |
| `output` | - | Output file path | Interactive prompt |
| `--format` | `-f` | Output format (text/markdown/html/json) | `text` |
| `--max-depth` | `-d` | Maximum depth to traverse | Unlimited |
| `--show-hidden` | `-a` | Show hidden files/directories | `False` |
| `--dirs-only` | - | Show directories only | `False` |
| `--show-size` | `-s` | Show file sizes | `False` |
| `--show-permissions` | `-p` | Show file permissions | `False` |
| `--ignore` | `-i` | Pattern to ignore (repeatable) | See defaults |
| `--verbose` | `-v` | Enable verbose logging | `False` |
| `--version` | - | Show version number | - |
| `--help` | `-h` | Show help message | - |

## Default Ignore Patterns

The tool automatically ignores these common directories and files:
- `__pycache__`, `.pytest_cache`, `.mypy_cache`
- `.git`, `.svn`, `.hg`
- `node_modules`
- `.idea`, `.vscode`
- `.DS_Store`
- `venv`, `env`
- `__MACOSX`

You can add more patterns with the `--ignore` flag.

## Output Examples

### Text Format with File Sizes
```bash
python directory_tree_generator.py ~/myproject tree.txt --show-size
```

Output:
```
myproject
├── src
│   ├── main.py (2.3KB)
│   ├── utils.py (1.5KB)
│   └── config.json (456B)
├── tests
│   └── test_main.py (3.1KB)
├── requirements.txt (124B)
└── README.md (5.7KB)
```

### Markdown Format
```bash
python directory_tree_generator.py ~/myproject tree.md --format markdown
```

Output:
```markdown
# myproject

- **src/**
  - main.py
  - utils.py
  - config.json
- **tests/**
  - test_main.py
- requirements.txt
- README.md
```

### Directories Only
```bash
python directory_tree_generator.py ~/myproject tree.txt --dirs-only -d 2
```

Output:
```
myproject
├── src
│   └── components
├── tests
└── docs
```

## Interactive Mode

If you don't provide command-line arguments, the tool enters interactive mode:

```bash
python directory_tree_generator.py
```

Interactive prompts:
```
Directory Tree Generator
==================================================

Enter the source directory path: /path/to/project
Enter the output file path (e.g., tree.txt): output.txt

Show hidden files? (y/n, default: n): n
Show directories only? (y/n, default: n): n

Output format:
1. Text (default)
2. Markdown
3. HTML
4. JSON
Choose format (1-4, default: 1): 1
```

## Use Cases

### 1. Project Documentation
Generate tree for README or documentation:
```bash
python directory_tree_generator.py ~/my-project docs/structure.md --format markdown
```

### 2. Code Review
Share project structure with team:
```bash
python directory_tree_generator.py ~/project review.txt --max-depth 3
```

### 3. Large Projects
Focus on main structure:
```bash
python directory_tree_generator.py ~/large-project tree.txt \
    --dirs-only \
    --max-depth 2 \
    --ignore build \
    --ignore dist
```

### 4. Web Visualization
Create HTML page:
```bash
python directory_tree_generator.py ~/project tree.html --format html --show-size
```

### 5. Data Analysis
Export as JSON for processing:
```bash
python directory_tree_generator.py ~/data structure.json --format json
```

### 6. Backup Planning
See full structure with sizes:
```bash
python directory_tree_generator.py ~/backup tree.txt \
    --show-size \
    --show-hidden
```

## Statistics Output

After generation, you'll see statistics:

```
==================================================
GENERATION STATISTICS
==================================================
Total directories: 45
Total files:       127
Errors:            2
==================================================

Output saved to: tree.txt
```

## Error Handling

The tool gracefully handles:
- **Permission denied**: Skips inaccessible directories
- **Deleted files**: Handles files removed during scan
- **Invalid paths**: Clear error messages
- **Write errors**: Checks output path before generation

Errors are counted and reported in statistics.

## Performance

- Efficiently handles large directory trees
- Memory-friendly (streaming output)
- Skip patterns to avoid processing unwanted directories
- Depth limiting for large hierarchies

## Project Structure

```
directory-tree-generator/
├── directory_tree_generator.py  # Main script
├── tree_README.md               # This file
├── requirements.txt             # Dependencies (none!)
├── setup.py                     # Package installation
├── LICENSE                      # MIT License
├── tests/                       # Unit tests
│   └── test_generator.py
└── examples/                    # Example outputs
    ├── example_text.txt
    ├── example_markdown.md
    ├── example_html.html
    └── example_json.json
```

## API Usage

Use as a Python module:

```python
from directory_tree_generator import DirectoryTreeGenerator, TreeConfig, OutputFormat

# Create configuration
config = TreeConfig(
    max_depth=3,
    show_hidden=False,
    show_size=True,
    ignore_patterns={'node_modules', '__pycache__'}
)

# Create generator
generator = DirectoryTreeGenerator(
    config=config,
    output_format=OutputFormat.MARKDOWN,
    verbose=True
)

# Generate to file
stats = generator.generate_to_file('/path/to/dir', 'output.md')

# Or get as string
tree_string = generator.generate_to_string('/path/to/dir')
print(tree_string)

# Print statistics
generator.print_stats()
```

## Comparison with Tree Command

| Feature | Unix `tree` | This Tool |
|---------|-------------|-----------|
| Cross-platform | Unix/Linux only | Python (all platforms) |
| Output formats | Text only | Text, Markdown, HTML, JSON |
| File sizes | Yes | Yes |
| Permissions | Yes | Yes |
| Ignore patterns | Limited | Extensive |
| Default ignores | No | Yes (node_modules, .git, etc.) |
| Interactive mode | No | Yes |
| API usage | No | Yes |
| Installation | System package | Python script |

## Troubleshooting

### "Permission denied" errors
Use `--verbose` to see which directories are being skipped:
```bash
python directory_tree_generator.py /path --verbose
```

### Output file already exists
The tool will overwrite existing files. Make sure the path is correct.

### Large directories taking too long
Use `--max-depth` to limit traversal:
```bash
python directory_tree_generator.py /large/dir tree.txt -d 3
```

### Too many files in output
Use `--dirs-only` or add ignore patterns:
```bash
python directory_tree_generator.py /dir tree.txt --dirs-only
python directory_tree_generator.py /dir tree.txt --ignore "*.log" --ignore "*.tmp"
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup
```bash
git clone <repository>
cd directory-tree-generator
pip install -r requirements-dev.txt
pytest tests/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Roadmap

Future enhancements:
- [ ] GUI version
- [ ] Git-aware tree (show only tracked files)
- [ ] File type statistics
- [ ] Size summaries by directory
- [ ] Color output for terminal
- [ ] Tree comparison (diff between directories)
- [ ] Custom styling for HTML output
- [ ] Export to other formats (XML, YAML)

## Author

[GitHub](https://github.com/Iammachino11)

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/Iammachino11/others/directory-tree/issues) on GitHub.