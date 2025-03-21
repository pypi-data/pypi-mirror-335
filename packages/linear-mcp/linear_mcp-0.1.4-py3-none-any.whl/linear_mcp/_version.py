"""Version information."""
import tomli

def get_version():
    """Get the version from pyproject.toml."""
    with open("pyproject.toml", "rb") as f:
        pyproject = tomli.load(f)
    return pyproject["project"]["version"]

__version__ = get_version()
