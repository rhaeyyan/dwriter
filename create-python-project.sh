#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

PROJECT_NAME=$1

if [ -z "$PROJECT_NAME" ]; then
    echo "Usage: create-python-project <project_name>"
    exit 1
fi

echo "🚀 Initializing project '$PROJECT_NAME' with uv..."

# Initialize the project using the src layout, python 3.12, and hatchling
uv init --lib --build-backend hatchling --python 3.12 "$PROJECT_NAME"
cd "$PROJECT_NAME"

echo "📦 Adding development dependencies (ruff, mypy, pytest)..."
uv add --dev ruff mypy pytest

echo "⚙️ Configuring pyproject.toml..."

# Append the configurations for Ruff, Mypy, and Pytest to pyproject.toml
cat << 'EOF' >> pyproject.toml

[tool.ruff]
target-version = "py312"
line-length = 88
src = ["src"]

[tool.ruff.lint]
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "N",  # pep8-naming
    "D",  # pydocstyle
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
    "UP", # pyupgrade
]
ignore = [
    "D100", # Missing docstring in public module
    "D104", # Missing docstring in public package
]

[tool.ruff.lint.per-file-ignores]
# Relax sensible rules in tests (e.g., allow assertions, ignore missing docstrings)
"tests/**/*" = ["S101", "D"]

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
check_untyped_defs = true
disallow_untyped_defs = true

[[tool.mypy.overrides]]
module = "tests.*"
# Do not strictly enforce type hinting on test functions
disallow_untyped_defs = false 

[tool.pytest.ini_options]
minversion = "8.0"
addopts = "-ra -q --strict-markers"
testpaths = ["tests"]
EOF

echo "📁 Setting up test directory..."
mkdir -p tests
touch tests/__init__.py

cat << 'EOF' > tests/test_basic.py
def test_example() -> None:
    assert True
EOF

echo "✅ Running initial validation checks..."
uv run ruff check .
uv run mypy src
uv run pytest

echo "✨ Project '$PROJECT_NAME' successfully bootstrapped!"
