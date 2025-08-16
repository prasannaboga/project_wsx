from pathlib import Path

def get_project_root() -> Path:
    """Return the project root directory (where pyproject.toml is located)."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    raise FileNotFoundError("Could not find project root (pyproject.toml not found)")
