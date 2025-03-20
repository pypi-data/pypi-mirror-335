#!/usr/bin/env bash
# Test script for argcomplete global registration

# Check if argcomplete is installed
if ! python3 -c "import argcomplete" 2>/dev/null; then
	echo "Error: argcomplete is not installed"
	echo "Install with: pip install argcomplete"
	exit 1
fi

# Check if the PYTHON_ARGCOMPLETE_OK marker is present in the entry point files
echo "Checking for PYTHON_ARGCOMPLETE_OK marker in entry point files:"
grep -l "PYTHON_ARGCOMPLETE_OK" src/dotcat/dotcat.py src/dotcat/__main__.py || echo "No marker found"

# Check if the dotcat executable is available
if ! which dotcat >/dev/null; then
	echo "Error: dotcat executable not found in PATH"
	echo "Make sure you have installed dotcat with 'pip install -e .'"
	exit 1
fi

# Check if register-python-argcomplete is available
if ! which register-python-argcomplete >/dev/null; then
	echo "Error: register-python-argcomplete not found in PATH"
	echo "Make sure you have installed argcomplete with 'pip install argcomplete'"
	exit 1
fi

# Output register-python-argcomplete for dotcat
echo "Running: register-python-argcomplete dotcat"
register-python-argcomplete dotcat

# Setup a test environment
echo -e "\nTo test interactively:"
echo "1. Run the following in your shell to register completion:"
echo "   eval \"\$(register-python-argcomplete dotcat)\""
echo "2. Then try completion with:"
echo "   dotcat /tmp/dotcat_test.json [TAB]"
echo ""
echo "You can also test global completion by activating it globally:"
echo "1. Run: activate-global-python-argcomplete"
echo "2. Source your shell config or start a new shell"
echo "3. Then try completion with dotcat"
