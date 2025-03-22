from pathlib import Path

from auto_name_enum import AutoNameEnum, auto


class OutputFormat(AutoNameEnum):
    json = auto()
    spaces = auto()
    lines = auto()


CACHE_DIR: Path = Path.home() / ".local/share/meta-fun"
