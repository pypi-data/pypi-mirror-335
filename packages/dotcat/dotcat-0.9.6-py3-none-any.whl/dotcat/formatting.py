"""
Output formatting functions for dotcat.
"""


def italics(text: str) -> str:
    """
    Returns the given text formatted in italics.

    Args:
        text: The text to format.

    Returns:
        The formatted text.
    """
    return f"\033[3m{text}\033[0m"


def bold(text: str) -> str:
    """
    Returns the given text formatted in bold.

    Args:
        text: The text to format.

    Returns:
        The formatted text.
    """
    return f"\033[1m{text}\033[0m"


def red(text: str) -> str:
    """
    Returns the given text formatted in red.

    Args:
        text: The text to format.

    Returns:
        The formatted text.
    """
    return f"\033[31m{text}\033[0m"
