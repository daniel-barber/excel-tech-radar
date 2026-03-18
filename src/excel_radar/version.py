"""Version information for excel-radar."""

import re
from pathlib import Path

def _get_version():
    """Read version from pyproject.toml."""
    try:
        # Try to find pyproject.toml (works in both dev and installed package)
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        if pyproject_path.exists():
            content = pyproject_path.read_text()
            match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
            if match:
                return match.group(1)
    except Exception:
        pass
    # Fallback version if pyproject.toml can't be read
    return "0.1.0"

__version__ = _get_version()

