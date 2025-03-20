#!/usr/bin/env python3
"""
Dotcat completion helper script.

This script extracts dotted paths from structured data files (JSON, YAML, TOML, INI)
to provide autocompletion suggestions for the dotcat command.

Usage:
    dotcat-completion.py <file> [prefix]

Arguments:
    file:   The file to extract paths from
    prefix: Optional prefix to filter paths (e.g., "project" to get "project.name",
            "project.version", etc.)

Output:
    A newline-separated list of dotted paths
"""

import sys
import os

# Import dotcat modules
try:
    from dotcat.parsers import parse_file
    from dotcat.data_access import LIST_ACCESS_SYMBOL
except ImportError:
    sys.stderr.write("Error: dotcat package not found. Please ensure it's installed.\n")
    sys.exit(1)


def extract_paths_from_data(data, prefix="", paths=None):
    """
    Recursively extract all possible dotted paths from parsed data.

    This is similar to the functionality in the main dotcat package but
    specialized for completion purposes.

    Args:
        data: The data to extract paths from
        prefix: The current path prefix
        paths: The set of paths found so far

    Returns:
        A set of all dotted paths in the data
    """
    if paths is None:
        paths = set()

    if isinstance(data, dict):
        for key, value in data.items():
            # Skip numeric keys
            if isinstance(key, str) and key.isdigit():
                continue

            current_path = f"{prefix}.{key}" if prefix else key
            paths.add(current_path)

            extract_paths_from_data(value, current_path, paths)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, dict):
                current_path = f"{prefix}{LIST_ACCESS_SYMBOL}{i}" if prefix else str(i)
                extract_paths_from_data(item, current_path, paths)

    return paths


def filter_paths_by_prefix(paths, prefix):
    """Filter paths by prefix and return the next segment."""
    if not prefix:
        # If no prefix, return top-level segments
        return {path.split(".")[0] for path in paths}

    # Find paths that start with the prefix
    matching_paths = {path for path in paths if path.startswith(prefix + ".")}

    # Extract the next segment after the prefix
    next_segments = set()
    prefix_len = len(prefix) + 1  # +1 for the dot

    for path in matching_paths:
        # Get the part after the prefix
        remainder = path[prefix_len:]
        # Get the next segment (up to the next dot)
        next_segment = remainder.split(".", 1)[0]
        if next_segment:
            next_segments.add(f"{prefix}.{next_segment}")

    return next_segments


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        sys.stderr.write(__doc__)
        sys.exit(1)

    file_path = sys.argv[1]
    prefix = sys.argv[2] if len(sys.argv) > 2 else ""

    if not os.path.isfile(file_path):
        sys.stderr.write(f"Error: File not found: {file_path}\n")
        sys.exit(1)

    try:
        # Use dotcat's parse_file function to parse the file
        data = parse_file(file_path)

        # Extract paths from the parsed data
        paths = extract_paths_from_data(data)
    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.exit(1)

    if prefix:
        # If we have a prefix, filter paths and get the next segments
        suggestions = sorted(filter_paths_by_prefix(paths, prefix))
        for suggestion in suggestions:
            print(suggestion)
    else:
        # If no prefix, get top-level segments
        top_level = sorted({path.split(".")[0] for path in paths})
        for path in top_level:
            print(path)


if __name__ == "__main__":
    main()
