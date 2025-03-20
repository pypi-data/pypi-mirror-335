#!/usr/bin/env bash
# Test script for argcomplete-based completion

# Ensure we're in the right directory
cd "$(dirname "$0")/.." || exit 1

# Check if argcomplete is installed
if ! python3 -c "import argcomplete" 2>/dev/null; then
	echo "Error: argcomplete is not installed"
	echo "Install with: pip install argcomplete"
	exit 1
fi

# Create a test JSON file if it doesn't exist
TEST_FILE="/tmp/dotcat_test.json"
if [ ! -f "$TEST_FILE" ]; then
	cat >"$TEST_FILE" <<EOF
{
    "project": {
        "name": "dotcat",
        "version": "0.9.5",
        "description": "Cat structured data, in style"
    },
    "dependencies": {
        "pyyaml": "6.0.2",
        "argcomplete": "3.2.1"
    },
    "settings": {
        "colors": {
            "enabled": true,
            "theme": "dark"
        },
        "output": {
            "format": "formatted",
            "indentation": 2
        }
    },
    "authors": [
        {
            "name": "John Doe",
            "email": "john@example.com"
        },
        {
            "name": "Jane Smith",
            "email": "jane@example.com"
        }
    ]
}
EOF
	echo "Created test file: $TEST_FILE"
fi

# Info about what we're testing
echo "Testing argcomplete-based completion for dotcat"
echo "Test file: $TEST_FILE"
echo ""
echo "The following line should show completion suggestions for 'dotcat $TEST_FILE '"
echo "Press Tab after typing the command to see completions"
echo ""

# Command to test completions with argcomplete
echo "Running: COMP_LINE=\"dotcat $TEST_FILE \" python -m argcomplete.completers"
echo ""

# Use argcomplete's debug mode to show completions - Fix for SC2097 and SC2098
export COMP_LINE="dotcat $TEST_FILE "
export COMP_POINT=${#COMP_LINE}
export _ARC_DEBUG=1
python -m argcomplete.completers

echo ""
echo "Test path completions for a specific prefix:"
echo "Running: COMP_LINE=\"dotcat $TEST_FILE project.\" python -m argcomplete.completers"
echo ""

# Test with a specific prefix - Fix for SC2097 and SC2098
export COMP_LINE="dotcat $TEST_FILE project."
export COMP_POINT=${#COMP_LINE}
export _ARC_DEBUG=1
python -m argcomplete.completers

echo ""
echo "You can also test interactively by running: dotcat $TEST_FILE [TAB]"
