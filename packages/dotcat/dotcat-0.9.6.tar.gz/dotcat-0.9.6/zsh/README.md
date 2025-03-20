# Dotcat Shell Completions

This directory contains files for shell completion support for the `dotcat`
command.

## Completion Options

Dotcat now supports three completion methods:

1. **Traditional ZSH Completion** - A custom ZSH completion script that provides
   basic file and dotted-path completions.
2. **Argcomplete-based Completion** - A more advanced completion system using
   Python's argcomplete library.
3. **Pipx Completions** - Automatic completions when installed via pipx.

## Installation

### Using pipx (Recommended)

The simplest way to install dotcat with completions is via pipx:

```bash
# Install dotcat
pipx install dotcat

# Make sure pipx completions are set up
pipx completions

# Follow the instructions from the command above to set up completions for your shell
```

### Automatic Installation

If you installed via pip or other methods, you can set up completions by
running:

```bash
dotcat-install-completions
```

This script will:

1. Attempt to install traditional ZSH completions if ZSH is detected
2. Attempt to set up argcomplete global completion if argcomplete is installed

### Manual Installation

#### Traditional ZSH Completion

1. Copy the `_dotcat` file to a directory in your `$fpath` (e.g.,
   `/usr/local/share/zsh/site-functions/`)
2. Copy `dotcat-completion.py` to a directory in your `$PATH`
3. Run `compinit` or restart your shell

#### Argcomplete-based Completion

1. Install argcomplete:

   ```bash
   pip install argcomplete
   ```

2. Activate global completion:

   ```bash
   activate-global-python-argcomplete
   ```

3. Source your shell configuration or restart your shell.

## How It Works

### Traditional Completion

The traditional ZSH completion uses the `_dotcat` file which calls the
`dotcat-completion.py` helper script. This script parses files and extracts
dotted paths to suggest as completions.

### Argcomplete Completion

The argcomplete-based completion uses Python's argcomplete library to provide
more intelligent completions. It leverages the existing code in dotcat to parse
files and suggest completions.

The main advantages of argcomplete are:

- It works with both ZSH and Bash
- It's integrated directly with the Python code, so it's more maintainable
- It can provide better context-aware completions

### pipx Completion

When installed via pipx with the `pipx completions` setup, dotcat will
automatically register for shell completion via argcomplete's entry point
system. This means:

- No additional setup is required beyond configuring pipx completions
- Works with zsh, bash, and other shells supported by pipx completions
- Updates automatically when dotcat is updated via pipx

## Choosing Between the Options

The recommended approach is to install via pipx. If you prefer other methods:

1. Argcomplete is preferred if available
2. Traditional ZSH completion is used as a fallback

If you have both installed, argcomplete will take precedence.

If you prefer to use only the traditional ZSH completion, you can remove
argcomplete:

```bash
pip uninstall argcomplete
```

## Files

- `_dotcat` - ZSH completion script (uses the Python helper)
- `dotcat-completion.py` - Python helper script for extracting dotted paths
- `test-completion.zsh` - Script for testing the completion locally

## Testing

You can test the completion by typing:

```bash
# Test file completion
dotcat [TAB]

# Test dotted path completion
dotcat path/to/file.json [TAB]

# Test nested path completion
dotcat path/to/file.json python[TAB]
```

For local testing without installation, use the test script:

```bash
./zsh/test-completion.zsh
```

## Troubleshooting

If completion doesn't work:

1. For pipx installation:

   - Make sure you've run `pipx completions` and followed the instructions
   - Restart your shell or source your shell configuration file

2. For traditional ZSH completion:

   - Make sure the file is in a directory in your $fpath
   - Check that the file has the correct permissions (chmod 755)
   - Run `compinit` to rebuild the completion system

3. For argcomplete:

   - Check that argcomplete is installed (`pip list | grep argcomplete`)
   - Make sure you've run `activate-global-python-argcomplete`
   - Restart your shell or source your shell configuration

4. Check for any error messages when sourcing your shell configuration file

## Manual Testing

If you want to test the Python helper script directly:

```bash
# Get top-level paths from a file
dotcat-completion.py path/to/file.json

# Get nested paths
dotcat-completion.py path/to/file.json python
dotcat-completion.py path/to/file.json python.editor
```

You can also use the included test script to try the completion in a temporary
environment:

```bash
# Run the test script
./zsh/test-completion.zsh
```
