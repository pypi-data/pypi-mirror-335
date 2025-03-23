from pathlib import Path
from typing import Optional


def file_exists(filepath: str) -> bool:
    return Path(filepath).is_file()


def directory_exists(dirpath: str) -> bool:
    return Path(dirpath).exists()


def create_directory(dirpath: str) -> None:
    Path(dirpath).mkdir(parents=True, exist_ok=True)


def get_file_timestamp(filepath: str) -> Optional[float]:
    return Path(filepath).stat().st_mtime


def safe_remove_file(filepath: str):
    Path(filepath).unlink(missing_ok=True)
