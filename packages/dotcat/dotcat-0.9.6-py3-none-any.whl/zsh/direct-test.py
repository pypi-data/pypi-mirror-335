#!/usr/bin/env python3
"""
Direct test of dotcat dotted path completion.
This tests the DottedPathCompleter directly without going through argcomplete.
"""

import os
import sys

from dotcat.completers import DottedPathCompleter
from dotcat.data_access import get_dotted_path_completions
from dotcat.parsers import parse_file


def main():
    """Test the DottedPathCompleter directly."""
    # Create test JSON file path
    test_file = "/tmp/dotcat_test.json"

    if not os.path.exists(test_file):
        print(
            "Test file {} does not exist. "
            "Please run ./zsh/test-argcomplete.sh first.".format(test_file)
        )
        sys.exit(1)

    # Test 1: Test basic file parser and get_dotted_path_completions
    print(f"Testing direct parser for file: {test_file}")
    try:
        data = parse_file(test_file)
        print("File parsed successfully.")

        # Get top-level completions
        completions = get_dotted_path_completions(data, "")
        print("\nTop-level completions:")
        for completion in sorted(completions):
            print(f"  - {completion}")

        # Get project-level completions
        project_completions = get_dotted_path_completions(data, "project")
        print("\nCompletions for 'project':")
        for completion in sorted(project_completions):
            print(f"  - {completion}")
    except Exception as e:
        print(f"Error parsing file or getting completions: {e}")
        sys.exit(1)

    # Test 2: Test the DottedPathCompleter directly
    print("\nTesting DottedPathCompleter class")
    completer = DottedPathCompleter()

    # Create a mock parsed_args object
    class MockArgs:
        file = test_file

    # Test with different prefixes
    test_prefixes = ["", "project", "settings", "authors"]

    for prefix in test_prefixes:
        print(f"\nCompletions for prefix '{prefix}':")
        try:
            completions = completer(prefix, MockArgs())
            for completion in sorted(completions):
                print(f"  - {completion}")
        except Exception as e:
            print(f"Error getting completions for '{prefix}': {e}")

    print("\nTesting complete.")


if __name__ == "__main__":
    main()
