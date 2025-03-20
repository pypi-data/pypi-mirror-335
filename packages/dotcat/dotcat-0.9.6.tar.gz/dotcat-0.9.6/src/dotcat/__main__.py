#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
"""
Entry point for running the dotcat package as a module.
This allows the package to be run with `python -m dotcat`.
"""

from dotcat.cli import main

if __name__ == "__main__":
    main()
