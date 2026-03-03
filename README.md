# Day Writer

A low-friction terminal journaling tool for tracking daily tasks and generating standup summaries.

## Features

- **Quick Logging**: Log tasks in seconds without leaving the terminal
- **Standup Generation**: Automatically format yesterday's entries for standup meetings
- **Weekly Reviews**: Generate summaries for sprint retrospectives or timesheets
- **Tagging & Projects**: Organize entries by tags and projects
- **Streak Tracking**: Gamify your logging habit
- **Configuration**: Customize formats, defaults, and display options
- **SQLite Storage**: Fast, reliable local storage

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### From Source (Recommended)

```bash
# Clone or navigate to the project directory
cd dwriter

# Create a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with dependencies
pip install -e .
```

### From Source (Development Mode)

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install with development dependencies (pytest, black, ruff)
pip install -e ".[dev]"
```

### Verify Installation

```bash
# Check the command is available
dwriter --version

# View help
dwriter --help
```

### Shell Completion (Optional)

```bash
# Bash - add to ~/.bashrc
echo 'source /path/to/dwriter/completions/day.bash' >> ~/.bashrc
source ~/.bashrc

# Zsh - add to ~/.zshrc
echo 'source /path/to/dwriter/completions/day.zsh' >> ~/.zshrc
source ~/.zshrc
```

## Usage

### Log a Task

```bash
# Basic logging
dwriter add "fixed the race condition in auth"

# With tags
dwriter add "fixed login bug" -t bug -t backend

# With project
dwriter add "implemented feature X" --project myapp

# Multiple tags
dwriter add "refactored database layer" -t refactor -t backend -p myapp
```

### View Entries

```bash
# Show today's entries
dwriter today

# Show all entries (default when running `dwriter` without arguments)
dwriter
```

### Generate Standup

```bash
# Generate yesterday's standup (copies to clipboard)
dwriter standup

# Different formats
dwriter standup --format slack
dwriter standup --format jira
dwriter standup --no-copy  # Don't copy to clipboard
```

### Review Period

```bash
# Review last 5 days (default)
dwriter review

# Review last 7 days
dwriter review --days 7

# Different output formats
dwriter review --format markdown
```

### Edit Entries

```bash
# Interactive edit/delete
dwriter edit

# Undo last entry
dwriter undo

# Bulk delete old entries
dwriter delete --before 2025-01-01
```

### Statistics

```bash
# Show logging stats and streak
dwriter stats
```

### Configuration

```bash
# View current config
dwriter config show

# Edit config file
dwriter config edit

# Reset to defaults
dwriter config reset

# Show config file path
dwriter config path
```

### Examples

```bash
# Show usage examples and workflows
dwriter examples
```

## Commands

| Command | Description |
|---------|-------------|
| `dwriter add "message"` | Add a new log entry |
| `dwriter today` | Show today's entries |
| `dwriter standup` | Generate yesterday's standup |
| `dwriter review --days N` | Review last N days |
| `dwriter edit` | Edit or delete entries |
| `dwriter undo` | Delete the most recent entry |
| `dwriter delete --before DATE` | Bulk delete old entries |
| `dwriter stats` | Show logging statistics |
| `dwriter config show` | View configuration |
| `dwriter config edit` | Edit configuration |
| `dwriter examples` | Show usage examples |
| `dwriter --help` | Show help message |

## Options for `add`

| Option | Description |
|--------|-------------|
| `-t, --tag` | Add a tag (can be used multiple times) |
| `-p, --project` | Set project name |

## Options for `standup`

| Option | Description |
|--------|-------------|
| `-f, --format` | Output format: bullets, slack, jira, markdown |
| `--no-copy` | Don't copy to clipboard |

## Options for `review`

| Option | Description |
|--------|-------------|
| `-d, --days` | Number of days to review (default: 5) |
| `-f, --format` | Output format: markdown, plain, slack |

## Configuration

Configuration is stored in `~/.day-writer/config.toml`.

### Standup Settings

```toml
[standup]
format = "bullets"  # bullets, slack, jira, markdown
copy_to_clipboard = true
```

### Review Settings

```toml
[review]
default_days = 5
format = "markdown"
```

### Display Settings

```toml
[display]
show_confirmation = true
show_id = true
colors = true
```

### Default Values

```toml
[defaults]
tags = ["work"]  # Default tags for all entries
project = "myapp"  # Default project
```

## Data Storage

Entries are stored in SQLite database at `~/.day-writer/entries.db`.

## Examples

### Morning Standup Workflow

```bash
# Throughout the day, log your tasks
dwriter add "reviewed PR #123"
dwriter add "fixed memory leak in cache module" -t bug
dwriter add "deployed to staging" -p backend

# Next morning, generate standup
dwriter standup
# Output is copied to clipboard, ready to paste in Slack
```

### Weekly Timesheet

```bash
# Generate weekly summary
dwriter review --days 7 --format markdown
```

### Set Default Project

```bash
# Edit config to set default project
dwriter config edit

# Add to config file:
# [defaults]
# project = "myapp"

# Now all entries will use this project by default
dwriter add "fixed bug"  # Automatically tagged with project "myapp"
```

## Development

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=dwriter

# Run linter
ruff check src/

# Format code
black src/
```

## License

MIT

## Troubleshooting

### Command Not Found

If you get `command not found: dwriter` after installation:

```bash
# Make sure the virtual environment is activated
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Verify installation
pip show dwriter
```

### Clipboard Not Working

If `dwriter standup` can't copy to clipboard:

- On Linux, ensure `xclip` or `xsel` is installed: `sudo apt install xclip`
- The standup output will be displayed in the terminal as a fallback

### Permission Errors

If you get permission errors during installation:

```bash
# Use a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# Or install with --user flag
pip install --user -e .
```
