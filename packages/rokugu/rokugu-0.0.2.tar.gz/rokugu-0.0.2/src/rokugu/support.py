from os import PathLike
from pathlib import Path
from typing import Union

from PySide6.QtCore import QStandardPaths


def standard_path(
    standard_location: QStandardPaths.StandardLocation,
    *other: Union[str, PathLike[str]],
) -> Path:
    """
    Args:
        standard_location: Lorem ipsum
        *other: Lorem ipsum
    Examples:

        standard_path(QStandardPaths.StandardLocation.AppDataLocation,'database.sqlite')
        /home/user/.local/share/example/database.sqlite
    """
    path = Path(QStandardPaths.writableLocation(standard_location))
    path.mkdir(parents=True, exist_ok=True)
    return path.joinpath(*other)


def file_size(size_in_bytes: float, precision: int = 2) -> str:
    units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]

    index = 0
    while (size_in_bytes / 1024) > 0.9 and (index < len(units) - 1):
        size_in_bytes /= 1024
        index += 1

    return f"{size_in_bytes:.{precision}f} {units[index]}"
