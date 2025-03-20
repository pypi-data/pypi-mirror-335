"""
Parsing functions for different file formats.
"""

import os
import tomllib
from io import StringIO
from configparser import ConfigParser
from typing import Any, Dict, List, Union

from .formatting import red

ParsedData = Union[Dict[str, Any], List[Any]]


class ParseError(Exception):
    """Custom exception for parsing errors."""

    pass


def parse_ini(file: StringIO) -> Dict[str, Dict[str, str]]:
    """
    Parses an INI file and returns its content as a dictionary.

    Args:
        file: The file object to parse.

    Returns:
        The parsed content as a dictionary.
    """

    config = ConfigParser()
    config.read_file(file)
    return {s: dict(config.items(s)) for s in config.sections()}


def parse_yaml(file: StringIO) -> ParsedData:
    """
    Parses a YAML file and returns its content.

    Args:
        file: The file object to parse.

    Returns:
        The parsed content.
    """
    import yaml

    try:
        return yaml.safe_load(file)
    except yaml.YAMLError as e:
        raise ParseError(f"Unable to parse YAML file: {str(e)}")


def parse_json(file: StringIO) -> ParsedData:
    """
    Parses a JSON file and returns its content.

    Args:
        file: The file object to parse.

    Returns:
        The parsed content.
    """
    import json

    try:
        return json.load(file)
    except json.JSONDecodeError as e:
        raise ParseError(f"Unable to parse JSON file: {str(e)}")


def parse_toml(file: StringIO) -> ParsedData:
    """
    Parses a TOML file and returns its content.

    Args:
        file: The file object to parse.

    Returns:
        The parsed content.
    """

    try:
        # tomllib requires bytes input, so we need to encode the string
        return tomllib.loads(file.read())
    except tomllib.TOMLDecodeError as e:
        raise ParseError(f"Unable to parse TOML file: {str(e)}")


FORMATS = [
    ([".json"], parse_json),
    ([".yaml", ".yml"], parse_yaml),
    ([".toml"], parse_toml),
    ([".ini"], parse_ini),
]


def parse_file(filename: str) -> ParsedData:
    """
    Tries to parse the file using different formats (JSON, YAML, TOML, INI).

    Args:
        filename: The name of the file to parse.

    Returns:
        The parsed content as a dictionary or list.
    """
    ext = os.path.splitext(filename)[1].lower()
    parsers = [parser for fmts, parser in FORMATS if ext in fmts]

    try:
        with open(filename, "r", encoding="utf-8") as file:
            content = file.read().strip()
            if not content:
                raise ValueError(f"{red('[ERROR]')} {filename}: File is empty")
            for parser in parsers:
                try:
                    return parser(StringIO(content))
                except ParseError as e:
                    # Re-raise with filename for better error message
                    raise ValueError(f"{str(e)}")
            msg = "Unsupported file format. Supported formats: JSON, YAML, TOML, INI"
            raise ValueError(f"{msg}")
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {red(filename)}")
    except Exception as e:
        # Capture the original error message
        error_msg = str(e)
        if (
            "JSONDecodeError" in error_msg
            or "YAMLError" in error_msg
            or "TOMLDecodeError" in error_msg
        ):
            raise ValueError("Unable to parse file")
        else:
            raise ValueError(f"Unable to parse file: {error_msg}")
