# dwriter - Developer & Configuration Guide 💻

This document contains configuration settings and developer-focused documentation for **dwriter**. For an overview of the tool and installation instructions, please refer to the [Main README](README.md).

---

## ⚙️ Configuration

Your settings are stored in `~/.dwriter/config.toml`. You can customize default projects, tags, output formats, and display preferences here.

**Example Config:**

```toml
[defaults]
project = "core-engine"
tags = ["dev"]

[standup]
format = "slack"
copy_to_clipboard = true

[review]
default_days = 7
format = "markdown"

[display]
show_confirmation = true
show_id = true
colors = true

```

**Configuration Options:**

| Section | Option | Description | Default |
| --- | --- | --- | --- |
| `[defaults]` | `project` | Default project for new entries | `null` |
| `[defaults]` | `tags` | Default tags for new entries | `[]` |
| `[standup]` | `format` | Default standup format (bullets, slack, jira, markdown) | `"bullets"` |
| `[standup]` | `copy_to_clipboard` | Auto-copy standup to clipboard | `true` |
| `[review]` | `default_days` | Default number of days to review | `5` |
| `[review]` | `format` | Default review format (markdown, plain, slack) | `"markdown"` |
| `[display]` | `show_confirmation` | Show confirmation after adding entries | `true` |
| `[display]` | `show_id` | Show entry IDs in output | `true` |
| `[display]` | `colors` | Enable colored output | `true` |

---

## 💻 Developer Commands

dwriter maintains **strict type safety** and **clean code standards** via mypy and ruff. All CI checks must pass before merging.

### Code Quality Status

| Tool | Status | Coverage |
|------|--------|----------|
| **mypy** | ✅ Strict mode | 27 source files, 0 errors |
| **ruff** | ✅ All checks | 0 errors |
| **pytest** | ✅ Test suite | All tests passing |

### Quick Start for Development

#### Using uv (Recommended)

```bash
# Install with dev dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Run type checking
uv run mypy src/

# Run linting
uv run ruff check src/ tests/

# Run the application
uv run dwriter --help
```

#### Using pip

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run type checking
mypy src/

# Run linting
ruff check src/ tests/

# Run the application
dwriter --help
```

### Development Workflow

**1. Making Changes**

```bash
# Edit your code
# ...

# Run type checking
uv run mypy src/

# Run linting (auto-fix when possible)
uv run ruff check src/ tests/ --fix

# Run tests
uv run pytest
```

**2. Before Committing**

```bash
# Ensure all checks pass
uv run mypy src/ && uv run ruff check src/ tests/ && uv run pytest
```

### Tool Configuration

All tooling is configured in [`pyproject.toml`](pyproject.toml):

- **mypy**: Strict mode with Python 3.9+ compatibility
- **ruff**: PEP-8, pydocstyle (Google convention), bugbear, pyupgrade
- **pytest**: Coverage enabled with `-v --cov=dwriter`

### Creating New Projects

dwriter includes a bootstrap script for creating new Python projects with the same tooling setup:

```bash
# Create a new project with uv, hatchling, ruff, mypy, and pytest pre-configured
./create-python-project.sh my_new_project
```

This script creates a project with:
- ✅ `uv` package manager with `hatchling` build backend
- ✅ Python 3.12 target
- ✅ `ruff` with comprehensive linting rules
- ✅ `mypy` in strict mode
- ✅ `pytest` configuration
- ✅ `src/` layout structure

---

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| **Type Coverage** | 100% (mypy strict) |
| **Lint Errors** | 0 |
| **Test Coverage** | Enabled via pytest-cov |
| **Python Versions** | 3.8 - 3.12 |
| **Dependencies** | 9 (click, tomlkit, pyperclip, sqlalchemy, rich, rapidfuzz, textual) |
| **Dev Dependencies** | 7 (pytest, pytest-cov, black, ruff, mypy, types-pyperclip, tomli) |

---

### 🐚 Shell Completions

dwriter includes shell completion scripts for Bash and Zsh for faster command entry.

**For Bash:**

```bash
source completions/day.bash

```

Add to your `~/.bashrc` for persistent completions.

**For Zsh:**

```bash
source completions/day.zsh

```

Add to your `~/.zshrc` for persistent completions.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

[Back to Main README](README.md)
