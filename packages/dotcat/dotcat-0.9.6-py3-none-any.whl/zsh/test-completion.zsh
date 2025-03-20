#!/usr/bin/env zsh
# shellcheck disable=SC1071  # ShellCheck only supports sh/bash/dash/ksh scripts, not zsh
# Test script for dotcat zsh completion

# Get the directory where this script is located
SCRIPT_DIR=${0:A:h}

# Set up a temporary environment
TEMP_DIR=$(mktemp -d)
echo "Setting up completion test environment in: $TEMP_DIR"

# Copy the completion script and Python helper to the temp directory
cp $SCRIPT_DIR/_dotcat $TEMP_DIR/_dotcat
cp $SCRIPT_DIR/dotcat-completion.py $TEMP_DIR/
chmod +x $TEMP_DIR/dotcat-completion.py

# Create a simple function to simulate the dotcat command
dotcat() {
  echo "dotcat $@"
  return 0
}

# Add the temp directory to fpath
fpath=($TEMP_DIR $fpath)

# Load the completion system
autoload -Uz compinit
compinit -D

# Source the completion script directly
source $TEMP_DIR/_dotcat

# Print instructions
cat << EOF

===== DOTCAT COMPLETION TEST =====

Test the following commands:

1. File completion:
   dotcat [TAB]

2. Basic dotted path completion:
   dotcat tests/fixtures/test.json [TAB]

3. Nested path completion:
   dotcat tests/fixtures/test.json python[TAB]
   dotcat tests/fixtures/test.json python.editor[TAB]

Press Ctrl+D to exit this test shell when done.
===================================

EOF

# Start a new interactive shell with the same options as the current shell
exec zsh -i
