"""A template for uv-based repositories."""

# spell-checker: words: uvrepotemplate

# Wheel names will be generated according to this value. Do not manually modify this value; instead
# update it according to committed changes by running this command from the root of the repository:
#
#   uv run python -m AutoGitSemVer.scripts.UpdatePythonVersion ./src/uvrepotemplate/__init__.py ./src
#
__version__ = "0.1.17"


def Add(
    a: int,
    b: int,
) -> int:
    """Add two values."""

    return a + b


def Subtract(
    a: int,
    b: int,
) -> int:
    """Subtract two values."""

    return a - b
