# dotcat: Cat Structured Data, in Style

Dealing with structured data in shell scripts is all but impossible.
`dotcat` gives you the ability to fetch structured data as easily as using cat it.

```bash
# Access data by attribute path
dotcat data.json person.name.first
# John
dotcat data.json person.name.last
# Doe

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
# ... from 5th to last item
```

## The good times are here

Easily read values from **JSON, YAML, TOML, and INI** files without complex scripting or manual parsing.

Access deeply **nested values** using intuitive dot-separated paths (e.g., **`person.first.name`**) while controlling the **output format** with `--output` flag.

Dotcat is a good **unix citizen** with well structured **exit codes** so it can take part of your command pipeline like cat or grep would.

Includes **ZSH autocompletion** for both file paths and dotted paths, making it even easier to navigate complex data structures.

## Installation

If you have a global pip install, this will install dotcat globally:

```bash
pip install dotcat
```

## ZSH Completion

Dotcat comes with ZSH completion support that is automatically installed when you install the package with pip. The installation script will:

1. Look for appropriate ZSH completion directories
2. Install the completion files if possible
3. Notify you of the installation location

If the automatic installation fails, you can manually install the completions:

```bash
# Copy the completion script to your ZSH completions directory
mkdir -p ~/.zsh/completions
cp /path/to/installed/package/zsh/_dotcat ~/.zsh/completions/

# Or run the installation script directly
dotcat-install-completions
```

See the [ZSH completion README](zsh/README.md) for detailed instructions.
