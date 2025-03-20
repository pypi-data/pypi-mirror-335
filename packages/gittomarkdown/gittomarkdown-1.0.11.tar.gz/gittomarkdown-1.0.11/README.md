# GitToMarkdown

A Python tool that automatically generates Markdown documentation from Git repositories. It creates comprehensive documentation including directory structure and file contents in a well-organized Markdown format.

## Features

- Clone and document Git repositories via HTTPS or SSH
- Concurrent processing of multiple repositories
- Generate directory tree structure in Markdown
- Include file contents with syntax highlighting
- Support for XML and JSON input files containing repository URLs
- Progress bars for clone and documentation generation
- Configurable thread count for parallel processing

## Installation

```bash
pip install gittomarkdown
```

## Usage

### Basic Usage

```python
from GitToMarkdown.GTM import GitToMark

# Document a single repository
repo = GitToMark("https://github.com/username/repository.git")
repo.generate

# Document multiple repositories
repos = GitToMark([
    "https://github.com/user1/repo1.git",
    "https://github.com/user2/repo2.git"
])
repos.generate
```

### Using SSH

```python
# Configure SSH key path first
GitToMark.config(ssh_path="/path/to/your/ssh/key")

# Clone and document using SSH
repo = GitToMark("git@github.com:username/repository.git", ssh=True)
repo.generate
```

### Batch Processing from Files

```python
# From XML file
repos = GitToMark.from_xml("repositories.xml")
repos.generate

# From JSON file
repos = GitToMark.from_json("repositories.json")
repos.generate

# From text file (one URL per line)
repos = GitToMark.from_file("repositories.txt")
repos.generate
```

### Configuration

```python
# Configure thread count and SSH key path
GitToMark.config(threads=8, ssh_path="/path/to/ssh/key")
```

## Directory Structure

- `GitToMarkdown/`: Main package directory
  - `GTM.py`: Core functionality
  - `Generator.py`: Markdown generation logic
  - `MarkdownUtils.py`: Markdown formatting utilities
  - `Parsers.py`: Input file parsers
  - `ProgressBar.py`: Progress bar implementation
  - `Zipper.py`: Repository compression utility
  - `errors.py`: Custom error definitions

## Output

The generated documentation will be saved in the `Output` directory with the following format:
- Repository tree structure
- File contents with syntax highlighting based on file extension
- Organized sections with clear headers

## Requirements

- Python 3.6+
- GitPython
- requests
- tqdm
- configparser

## License

This project is under the MIT License.