#!/usr/bin/env bash
# Test script for pipx completions with dotcat

set -e

echo "Testing pipx completion integration for dotcat"
echo "---------------------------------------------"

# Check if pipx is installed
if ! command -v pipx &>/dev/null; then
	echo "Error: pipx is not installed. Please install pipx first."
	exit 1
fi

# Check if argcomplete is installed
if ! python3 -c "import argcomplete" &>/dev/null; then
	echo "Error: argcomplete is not installed. Please install it:"
	echo "    pip install argcomplete"
	exit 1
fi

# Build the current version of the package
echo "Building the package..."
cd "$(dirname "$(dirname "$0")")" # Go to the project root
python -m build --wheel

# Find the built wheel
WHEEL=$(ls -t dist/*.whl | head -1)
if [ -z "$WHEEL" ]; then
	echo "Error: Could not find a wheel in the dist directory."
	exit 1
fi

echo "Using wheel: $WHEEL"

# Create a temporary directory
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

# Create a virtual environment for testing
echo "Creating a test environment..."
python -m venv "$TEMP_DIR/venv"
source "$TEMP_DIR/venv/bin/activate"

# Install argcomplete in the test environment
pip install argcomplete

# Install the package in development mode
pip install -e .

# Test that the register_completions function is available
echo "Testing completion registration..."
python -c "from zsh import register_completions; print('Success: register_completions function found')"

# Test the register_completions function
echo "Testing completion registration function..."
python -c "from zsh import register_completions; parser = register_completions(); print(f'Success: Parser created: {parser is not None}')"

# Verify the entry point is correctly configured
echo "Checking argcomplete entry point..."
if grep -q "project.entry-points.argcomplete" pyproject.toml; then
	echo "Success: argcomplete entry point found in pyproject.toml"
else
	echo "Error: argcomplete entry point not found in pyproject.toml"
	exit 1
fi

# Check that the script is marked for argcomplete
echo "Checking for PYTHON_ARGCOMPLETE_OK markers..."
if grep -q "PYTHON_ARGCOMPLETE_OK" src/dotcat/dotcat.py; then
	echo "Success: PYTHON_ARGCOMPLETE_OK marker found in dotcat.py"
else
	echo "Error: PYTHON_ARGCOMPLETE_OK marker not found in dotcat.py"
	exit 1
fi

echo ""
echo "All tests passed! The package is ready for pipx completions."
echo ""
echo "To install with pipx:"
echo "    pipx install $WHEEL"
echo ""
echo "To set up completions:"
echo "    pipx completions"
echo ""
echo "Follow the instructions from the pipx completions command to set up your shell."

deactivate # Deactivate the virtual environment
