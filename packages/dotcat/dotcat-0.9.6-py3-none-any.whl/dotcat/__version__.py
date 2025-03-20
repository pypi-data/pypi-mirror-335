from importlib import metadata
import pathlib
import tomllib


def get_version_from_toml():
    """
    Extract version from pyproject.toml file.

    Returns:
        str: The version string or "unknown" if not found
    """
    try:
        # Find the project root (where pyproject.toml is located)
        current_file = pathlib.Path(__file__)
        project_root = (
            current_file.parent.parent.parent
        )  # src/dotcat -> src -> project root
        pyproject_path = project_root / "pyproject.toml"

        if pyproject_path.exists():
            # Parse pyproject.toml using the toml library
            pyproject_data = tomllib.load(pyproject_path.open("rb"))
            return pyproject_data.get("project", {}).get("version", "unknown")
    except Exception:
        pass
    return "unknown"


# Try to get version from package metadata (works when installed)
try:
    __version__ = metadata.version("dotcat")
except metadata.PackageNotFoundError:
    # Fallback: read version from pyproject.toml (works during development/CI)
    __version__ = get_version_from_toml()

# Make the function available for testing
__all__ = ["get_version_from_toml"]
