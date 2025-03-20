"""
Command-line interface functions for dotcat.
"""

import sys
import os
import argparse
from typing import List, Tuple, Optional

# Add import for argcomplete
try:
    import argcomplete

    HAS_ARGCOMPLETE = True
except ImportError:
    HAS_ARGCOMPLETE = False

from .__version__ import __version__
from .formatting import red
from .help_text import HELP, USAGE
from .core import is_likely_dot_path, process_file, lookup_value, format_value

# Import the completers module
try:
    from .completers import setup_completers
except ImportError:
    # Define a no-op function if the module is not available
    def setup_completers(parser):
        pass


def handle_version_flag(version_flag: bool) -> bool:
    """
    Handle the version flag if present.

    Args:
        version_flag: Whether the version flag was provided.

    Returns:
        True if the version flag was handled, False otherwise.
    """
    if version_flag:
        print(f"dotcat version {__version__}")
        return True
    return False


def handle_special_case_arguments(
    filename: str, lookup_chain: str, args: List[str]
) -> Tuple[str, str]:
    """
    Handle special case where a single argument looks like a dotted-path.

    Args:
        filename: The filename argument.
        lookup_chain: The dotted-path argument.
        args: The original command-line arguments.

    Returns:
        The updated filename and lookup_chain.
    """
    # Special case: If we have only one argument and it looks like a dotted-path,
    # treat it as the dotted-path rather than the file
    if filename is not None and lookup_chain is None and len(args) == 1:
        if is_likely_dot_path(filename):
            # Swap the arguments
            lookup_chain = filename
            filename = None

    return filename, lookup_chain


def validate_required_arguments(
    filename: str, lookup_chain: str, args: List[str]
) -> None:
    """
    Validate that the required arguments are present.

    Args:
        filename: The filename argument.
        lookup_chain: The dotted-path argument.
        args: The original command-line arguments.

    Raises:
        SystemExit: If required arguments are missing.
    """
    if lookup_chain is None or filename is None:
        if filename is not None and lookup_chain is None:
            # Case 1: File is provided but dotted-path is missing
            try:
                if os.path.exists(filename):
                    # File exists, but dotted-path is missing
                    print(
                        f"Dotted-path required. Which value do you want me "
                        f"to look up in {filename}?"
                    )
                    print(f"\n$dotcat {filename} {red('<dotted-path>')}")
                    sys.exit(2)  # Invalid usage
            except Exception:
                # If there's any error checking the file,
                # fall back to general usage message
                pass
        elif filename is None and lookup_chain is not None:
            # Case 2: Dotted-path is provided but file is missing
            # Check if the argument looks like a dotted-path (contains dots)
            if "." in lookup_chain:
                # It looks like a dotted-path, so assume the file is missing
                print(
                    f"File path required. Which file contains the value "
                    f"at {lookup_chain}?"
                )
                print(f"\n$dotcat {red('<file>')} {lookup_chain}")
                sys.exit(2)  # Invalid usage
            # Otherwise, it might be a file without an extension or something else,
            # so fall back to the general usage message

        # General usage message for other cases
        print(USAGE)  # Display usage for invalid arguments
        sys.exit(2)  # Invalid usage


def process_and_display_result(
    filename: str, lookup_chain: str, output_format: str
) -> None:
    """
    Process the file, look up the value, and display the result.

    Args:
        filename: The file to process.
        lookup_chain: The dotted-path to look up.
        output_format: The output format.

    Raises:
        SystemExit: If there's an error processing the file or looking up the value.
    """
    try:
        data = process_file(filename)
    except FileNotFoundError as e:
        print(str(e))
        sys.exit(3)  # File not found
    except ValueError as e:
        print(str(e))
        sys.exit(4)  # Parsing error

    try:
        value = lookup_value(data, lookup_chain)
        formatted_value = format_value(value, output_format)
        print(formatted_value)
    except KeyError as e:
        key = e.args[0].split("'")[1] if "'" in e.args[0] else e.args[0]
        print(f"Key {red(key)} not found in {filename}")
        sys.exit(5)  # Key not found


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create and return the argument parser.

    This function is separated to allow reuse by the argcomplete registration.

    Returns:
        The configured argument parser
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("file", type=str, nargs="?", help="The file to read from")
    parser.add_argument(
        "dotted_path",
        type=str,
        nargs="?",
        help="The dotted-path to look up",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="raw",
        help="The output format (raw, formatted, json, yaml, toml, ini)",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information",
    )

    # Set up custom completers
    setup_completers(parser)

    return parser


def parse_args(args: List[str]) -> Tuple[Optional[str], Optional[str], str, bool]:
    """
    Returns the filename, dotted-path, output format, and version flag.

    Args:
        args: The list of command-line arguments.

    Returns:
        The filename, dotted-path, output format, and version flag.
    """
    # Handle help commands
    if args is None or len(args) == 0:
        print(HELP)  # Show help for no arguments
        sys.exit(0)

    # Handle explicit help requests
    if "help" in args or "-h" in args or "--help" in args:
        print(HELP)  # Show help for help requests
        sys.exit(0)

    parser = create_argument_parser()

    # Enable argcomplete if available
    if HAS_ARGCOMPLETE:
        argcomplete.autocomplete(parser)

    parsed_args = parser.parse_args(args)
    return (
        parsed_args.file,
        parsed_args.dotted_path,
        parsed_args.output,
        parsed_args.version,
    )


def run(args: List[str] = None) -> None:
    """
    Processes the command-line arguments and prints the value from the
    structured data file.

    Args:
        args: The list of command-line arguments.
    """
    # validates arguments
    filename, lookup_chain, output_format, version_flag = parse_args(args)

    # Handle version flag
    if handle_version_flag(version_flag):
        return  # Exit early if version flag was handled

    # Handle special case arguments
    filename, lookup_chain = handle_special_case_arguments(filename, lookup_chain, args)

    # Validate required arguments (passing args for context)
    validate_required_arguments(filename, lookup_chain, args)

    # Process the file, look up the value, and display the result
    process_and_display_result(filename, lookup_chain, output_format)


def main() -> None:
    """
    The main entry point of the script.
    """
    run(sys.argv[1:])
