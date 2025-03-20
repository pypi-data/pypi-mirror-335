import sys
from pathlib import Path
from typing import Union


def base_path(path: Union[Path, str]):
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS).joinpath(path)

    return Path().cwd().joinpath(path)
