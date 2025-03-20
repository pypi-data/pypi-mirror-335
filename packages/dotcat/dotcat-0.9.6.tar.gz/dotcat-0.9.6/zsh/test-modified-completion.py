#!/usr/bin/env python3
"""
Test script for the modified dotcat-completion.py
"""

import sys
import os
import subprocess


def test_completion():
    """Test the modified completion script with a sample file."""
    # Path to the completion script
    script_path = os.path.join(os.path.dirname(__file__), "dotcat-completion.py")

    # Path to a test file
    test_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "tests", "fixtures", "test.json"
    )

    # Ensure the test file exists
    if not os.path.exists(test_file):
        print(f"Test file not found: {test_file}")
        return False

    # Run the completion script
    try:
        result = subprocess.run(
            [sys.executable, script_path, test_file],
            capture_output=True,
            text=True,
            check=True,
        )

        # Check if we got some output
        if result.stdout.strip():
            print("Test passed! Output:")
            print(result.stdout)
            return True
        else:
            print("Test failed: No output received")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Test failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


if __name__ == "__main__":
    success = test_completion()
    sys.exit(0 if success else 1)
