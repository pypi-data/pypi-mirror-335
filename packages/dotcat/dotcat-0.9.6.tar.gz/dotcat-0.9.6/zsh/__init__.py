"""
Zsh completions for dotcat.
"""

from .install_completions import main as install_completions_main


def register_completions():
    """
    Register argcomplete completions.
    This function is called by pipx to register completions.
    """
    try:
        import argcomplete
        from argcomplete.completers import FilesCompleter
        import argparse

        from dotcat.completers import DottedPathCompleter

        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument(
            "file", type=str, nargs="?", help="The file to read from"
        ).completer = FilesCompleter()
        parser.add_argument(
            "dotted_path",
            type=str,
            nargs="?",
            help="The dotted-path to look up",
        ).completer = DottedPathCompleter()
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

        # Register the parser with argcomplete
        argcomplete.autocomplete(parser)
        return parser
    except ImportError:
        # If argcomplete is not available, return None
        return None


__all__ = ["install_completions_main", "register_completions"]
