"""
Core logic functions for dotcat.
"""

import os
from typing import Any

from .formatting import red
from .parsers import parse_file
from .data_access import from_dotted_path
from .output_formatters import format_output


def is_likely_dot_path(arg: str) -> bool:
    """
    Determines if an argument is likely a dotted-path rather than a file path.

    Args:
        arg: The argument to check.

    Returns:
        True if the argument is likely a dot path, False otherwise.
    """
    # If it contains dots and doesn't look like a file path
    if "." in arg and not os.path.exists(arg):
        # Check if it has multiple segments separated by dots
        return len(arg.split(".")) > 1
    return False


def process_file(filename: str) -> Any:
    """
    Parse the file and handle any errors.

    Args:
        filename: The file to parse.

    Returns:
        The parsed data.

    Raises:
        FileNotFoundError: If the file is not found.
        ValueError: If there's an error parsing the file.
    """
    try:
        return parse_file(filename)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {red(filename)}")
    except ValueError as e:
        if "File is empty" in str(e):
            raise ValueError(f"{red('[ERROR]')} {filename}: File is empty")
        elif "Unable to parse file" in str(e):
            raise ValueError(f"Unable to parse file: {red(filename)}")
        else:
            raise ValueError(f"{str(e)}: {red(filename)}")


def lookup_value(data: Any, lookup_chain: str) -> Any:
    """
    Look up the value using the dotted-path.

    Args:
        data: The parsed data.
        lookup_chain: The dotted-path to look up.

    Returns:
        The value at the specified path.

    Raises:
        KeyError: If the key is not found.
    """
    return from_dotted_path(data, lookup_chain)


def format_value(value: Any, output_format: str) -> str:
    """
    Format the value according to the specified output format.

    Args:
        value: The value to format.
        output_format: The output format.

    Returns:
        The formatted value.
    """
    return format_output(value, output_format)
