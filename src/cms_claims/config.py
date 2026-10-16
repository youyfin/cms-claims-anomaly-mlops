from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_config(path: str | Path) -> dict[str, Any]:
    '''
    Load the config file as a dictionary
    '''
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)                                            # Load the config file as a dictionary


def resolve_project_path(project_root: Path, value: str) -> Path:
    '''
    To automatically resolve relative paths to absolute paths based on the project root, ensuring file paths remain reliable regardless of the current working directory.
    '''
    path = Path(value)
    return path if path.is_absolute() else project_root / path
