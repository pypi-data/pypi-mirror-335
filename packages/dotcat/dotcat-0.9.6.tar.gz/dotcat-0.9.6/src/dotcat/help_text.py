"""
Help text for dotcat.
"""

from .formatting import bold

# Usage text
USAGE = f"""
{bold('dotcat')}
Read values from structured data files (JSON, YAML, TOML, INI)

  Usage: dotcat <file> <dotted-path>

    <file>          The input file (JSON, YAML, TOML, INI).
    <dotted-path>   The dotted path to the desired data (e.g., project.authors).

{bold('EXAMPLES:')}
  dotcat config.json python.editor.tabSize
  dotcat pyproject.toml project.version
  dotcat package.json dependencies.react

  dotcat --version
  See `dotcat --help` for more information.
"""

# Core help text
HELP_CORE = (
    USAGE
    + f"""

{bold('OPTIONS:')}
  --version       Show version information
  --help          Show this help message and exit"""
)

# Example help text
HELP_EXAMPLE = """
    # Access data by attribute path
    dotcat data.json person.name.first

    # John
    dotcat data.json person.name.last # Doe

    # Controle your output format
    dotcat data.json person.name --output=yaml

    # name:
    #   first: John
    #   last: Doe
    dotcat data.json person.name --output=json
    # {"first": "John", "last": "Doe"}
    # List access
    dotcat data.json person.friends@0

    # {"name":{"first": "Alice", "last": "Smith"}, "age": 25} -> item access
    dotcat data.json person.friends@2:4

    # [{"name":{"first": "Alice", "last": "Smith"}, "age": 25}, {"name":{"first": "Bob", "last": "Johnson"}, "age": 30}]  -> slice access
    dotcat data.json person.friends@4:-1
"""

# Complete help text
HELP = HELP_CORE + HELP_EXAMPLE
