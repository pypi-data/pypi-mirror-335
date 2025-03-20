#!/usr/bin/env python3
"""
Script to install zsh completions for dotcat.
This script is run during package installation.
"""

import os
import shutil
import subprocess
import sys


def is_zsh_available():
    """Check if zsh is available on the system."""
    try:
        subprocess.run(
            ["zsh", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        return True
    except FileNotFoundError:
        return False


def is_argcomplete_available():
    """Check if argcomplete is available."""
    try:
        # Check if argcomplete can be imported
        __import__("argcomplete")
        return True
    except ImportError:
        return False


def is_pipx_available():
    """Check if pipx is available on the system."""
    try:
        subprocess.run(
            ["pipx", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        return True
    except FileNotFoundError:
        return False


def get_zsh_completion_dirs():
    """Get potential zsh completion directories."""
    # Common system-wide completion directories
    system_dirs = [
        "/usr/share/zsh/site-functions",
        "/usr/local/share/zsh/site-functions",
    ]

    # User-specific completion directories
    home = os.path.expanduser("~")
    user_dirs = [
        os.path.join(home, ".zsh", "completions"),
        os.path.join(home, ".oh-my-zsh", "completions"),
        os.path.join(home, ".zsh", "site-functions"),
    ]

    # Check which directories exist and are writable
    valid_dirs = []

    # First check user directories (preferred)
    for d in user_dirs:
        if not os.path.exists(d):
            try:
                os.makedirs(d, exist_ok=True)
                valid_dirs.append(d)
            except (OSError, PermissionError):
                continue
        elif os.access(d, os.W_OK):
            valid_dirs.append(d)

    # Then check system directories if running with sufficient privileges
    if not valid_dirs:
        for d in system_dirs:
            if os.path.exists(d) and os.access(d, os.W_OK):
                valid_dirs.append(d)

    return valid_dirs


def setup_argcomplete():
    """Set up argcomplete for dotcat."""
    if not is_argcomplete_available():
        print("argcomplete not found, skipping argcomplete setup.")
        return False

    try:
        # Try to run activate-global-python-argcomplete
        print("Setting up argcomplete global completion...")

        # Check if activate-global-python-argcomplete is available
        try:
            subprocess.run(
                ["which", "activate-global-python-argcomplete"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(
                "activate-global-python-argcomplete not found, "
                "skipping argcomplete setup."
            )
            return False

        # Run activate-global-python-argcomplete
        subprocess.run(
            ["activate-global-python-argcomplete"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

        print("argcomplete global completion setup successful.")

        # Tell the user to source their shell config
        shell = os.environ.get("SHELL", "").split("/")[-1]
        if shell == "zsh":
            print(
                "Please run 'source ~/.zshrc' to enable completions in your "
                "current session."
            )
        elif shell == "bash":
            print(
                "Please run 'source ~/.bashrc' to enable completions in your "
                "current session."
            )
        else:
            print("Please restart your shell to enable completions.")

        return True
    except Exception as e:
        print(f"Error setting up argcomplete: {e}")
        return False


def check_pipx_installation():
    """Check if dotcat was installed via pipx and provide guidance."""
    if is_pipx_available():
        try:
            # Check if dotcat is installed via pipx
            result = subprocess.run(
                ["pipx", "list"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True,
            )

            if "dotcat" in result.stdout:
                print("\nDetected pipx installation of dotcat.")
                print("For the best completion experience with pipx:")
                print("1. Run: pipx completions")
                print("2. Follow the instructions from that command")
                print("3. Restart your shell or source your shell configuration file")
                return True

        except subprocess.CalledProcessError:
            pass

    return False


def install_completions():
    """Install zsh completions."""
    # First check if we're using pipx
    if check_pipx_installation():
        # If dotcat is installed via pipx, focus on that method
        if setup_argcomplete():
            print("argcomplete global setup successful as a fallback.")
        return

    if not is_zsh_available():
        print("ZSH not found. Skipping traditional zsh completion installation.")
        # Try to set up argcomplete anyway
        if setup_argcomplete():
            print(
                "argcomplete setup successful, dotcat will use argcomplete "
                "instead of traditional completion."
            )
            return
        print("Fallback: You can manually set up completions or install argcomplete.")
        return

    # Get the directory where this script is located (zsh/)
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Path to the completion files (already in the zsh directory)
    completion_script = os.path.join(script_dir, "_dotcat")
    helper_script = os.path.join(script_dir, "dotcat-completion.py")

    if not os.path.exists(completion_script):
        print(
            f"Completion script not found at {completion_script}. "
            "Skipping installation."
        )
        # Try to set up argcomplete
        if setup_argcomplete():
            print(
                "argcomplete setup successful, dotcat will use argcomplete "
                "instead of traditional completion."
            )
            return
        return

    # Find a suitable completion directory
    completion_dirs = get_zsh_completion_dirs()
    if not completion_dirs:
        print("No suitable zsh completion directory found. Trying argcomplete instead.")
        if setup_argcomplete():
            print(
                "argcomplete setup successful, dotcat will use argcomplete "
                "instead of traditional completion."
            )
            return
        print(f"Completion files are located at: {script_dir}")
        return

    # Install the completion script
    target_dir = completion_dirs[0]
    target_completion = os.path.join(target_dir, "_dotcat")

    try:
        shutil.copy2(completion_script, target_completion)
        os.chmod(target_completion, 0o755)  # Make executable
        print(f"Installed traditional zsh completion to {target_completion}")

        # Install the helper script if possible
        if os.path.exists(helper_script):
            # Try to find a directory in PATH
            path_dirs = os.environ.get("PATH", "").split(os.pathsep)
            user_bin = os.path.expanduser("~/bin")

            # Create ~/bin if it doesn't exist
            if not os.path.exists(user_bin):
                try:
                    os.makedirs(user_bin, exist_ok=True)
                    path_dirs.insert(0, user_bin)
                except OSError:
                    pass

            # Find a writable directory in PATH
            target_helper = None
            for d in path_dirs:
                if os.path.exists(d) and os.access(d, os.W_OK):
                    target_helper = os.path.join(d, "dotcat-completion.py")
                    break

            if target_helper:
                shutil.copy2(helper_script, target_helper)
                os.chmod(target_helper, 0o755)  # Make executable
                print(f"Installed completion helper to {target_helper}")
            else:
                print(
                    "Could not find a writable directory in PATH for the helper script."
                )
                print(f"Please install the helper script manually from {helper_script}")

        # Try to set up argcomplete as well for better completion
        setup_argcomplete()

    except (OSError, PermissionError) as e:
        print(f"Error installing traditional completions: {e}")
        print("Trying argcomplete instead...")
        if setup_argcomplete():
            print(
                "argcomplete setup successful, dotcat will use argcomplete "
                "instead of traditional completion."
            )
            return
        print(f"Please install completions manually from {script_dir}")


def main():
    """Main entry point."""
    print("\n=== Dotcat Completion Setup ===\n")

    try:
        install_completions()

        # Final recommendations
        print("\nRecommendations for the best experience:")
        print("1. If using pipx: Run 'pipx completions' and follow the instructions")
        print("2. If using pip: Make sure argcomplete is installed and activated")
        print("3. Restart your shell or source your shell configuration file")

    except Exception as e:
        print(f"Error during completion installation: {e}")
        # Don't fail the installation if completion setup fails
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
