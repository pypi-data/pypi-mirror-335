from pathlib import Path
from typing import List


def is_local_path(path: str):
    return Path(path).exists()


def list_files(dir: Path) -> List[str]:
    """List files that are immediate children of the directory."""
    return [f.name for f in dir.iterdir() if f.is_file()]


def list_dirs(dir: Path) -> List[str]:
    return [f.name for f in dir.iterdir() if f.is_dir()]


def safe_mkdir(dir: Path) -> None:
    """Creates a directory, making parents if necessary and passing if the directory already exists."""
    if not dir.exists():
        dir.mkdir(parents=True, exist_ok=True)
