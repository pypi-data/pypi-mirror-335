"""
Custom completers for dotcat using argcomplete.
"""

import os
from typing import Any, List

from .parsers import parse_file
from .data_access import get_dotted_path_completions


class DottedPathCompleter:
    """
    Completer for dotted paths based on the content of a file.

    Uses the parsed content of the file specified by the 'file' argument
    to suggest completions for the dotted-path argument.
    """

    def __call__(self, prefix: str, parsed_args: Any, **kwargs: Any) -> List[str]:
        """
        Generate completions for a dotted path based on a file's content.

        Args:
            prefix: The prefix text of the current word being completed
            parsed_args: The argparse namespace with parsed arguments so far
            **kwargs: Additional keyword arguments provided by argcomplete

        Returns:
            List of possible completions
        """
        if not hasattr(parsed_args, "file") or not parsed_args.file:
            return []

        file_path = parsed_args.file

        # Check if the file exists
        if not os.path.isfile(file_path):
            return []

        try:
            # Parse the file and get its data
            data = parse_file(file_path)

            # Get completions using the existing function
            completions = get_dotted_path_completions(data, prefix or "")

            return completions
        except Exception:
            # If there's any error parsing the file or getting completions,
            # return an empty list to not interfere with command line usage
            return []


def setup_completers(parser: Any) -> None:
    """
    Set up completers for a parser.

    Args:
        parser: The argparse parser to add completers to
    """
    try:
        # Import here to avoid dependency on argcomplete for core functionality
        from argcomplete.completers import FilesCompleter

        # Find the file argument and set its completer to FilesCompleter
        for action in parser._actions:
            if getattr(action, "dest", None) == "file":
                action.completer = FilesCompleter()
            elif getattr(action, "dest", None) == "dotted_path":
                action.completer = DottedPathCompleter()
    except ImportError:
        # If argcomplete is not available, do nothing
        pass
