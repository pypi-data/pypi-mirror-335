#! /usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
"""
This script reads values, including nested values, from structured data files
(JSON, YAML, TOML, INI).

Usage:
    dotcat <file> <dotted-path>

Example:
    dotcat config.json python.editor.tabSize
    dotcat somefile.toml a.b.c

Exit Codes:
    2: Invalid usage (wrong number of arguments)
    3: File not found
    4: Parsing error
    5: Key not found
"""

# Import from modules
from .formatting import italics, bold, red
from .help_text import USAGE, HELP_CORE, HELP_EXAMPLE, HELP
from .parsers import (
    ParseError,
    parse_ini,
    parse_yaml,
    parse_json,
    parse_toml,
    FORMATS,
    parse_file,
    ParsedData,
)
from .output_formatters import format_output
from .data_access import LIST_ACCESS_SYMBOL, SLICE_SYMBOL, access_list, from_dotted_path
from .cli import parse_args, is_likely_dot_path, run, main

# For backward compatibility, re-export everything
__all__ = [
    "italics",
    "bold",
    "red",
    "USAGE",
    "HELP_CORE",
    "HELP_EXAMPLE",
    "HELP",
    "ParseError",
    "parse_ini",
    "parse_yaml",
    "parse_json",
    "parse_toml",
    "FORMATS",
    "parse_file",
    "ParsedData",
    "format_output",
    "LIST_ACCESS_SYMBOL",
    "SLICE_SYMBOL",
    "access_list",
    "from_dotted_path",
    "parse_args",
    "is_likely_dot_path",
    "run",
    "main",
]

if __name__ == "__main__":
    main()
