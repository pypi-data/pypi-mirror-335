from functools import lru_cache
from pathlib import Path
from typing import Any, Optional
import tomllib


@lru_cache
def load_pyproject_config() -> Optional[dict[str, Any]]:
    pyproject_path = _find_pyproject_toml()
    if not pyproject_path:
        return None

    with open(pyproject_path, "rb") as f:
        return tomllib.load(f)


@lru_cache
def _find_pyproject_toml() -> Optional[Path]:
    current = Path.cwd()
    while current != current.parent:
        pyproject_path = current / "pyproject.toml"
        if pyproject_path.exists():
            return pyproject_path
        current = current.parent
    return None