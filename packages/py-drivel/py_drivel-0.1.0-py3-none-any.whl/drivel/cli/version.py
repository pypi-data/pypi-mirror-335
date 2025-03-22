from pathlib import Path
from importlib import metadata

import toml


def get_version_from_metadata() -> str:
    return metadata.version(__package__ or __name__)


def get_version_from_pyproject() -> str:
    toml_path = Path("pyproject.toml")
    return toml.loads(toml_path.read_text())["project"]["version"]


def get_version() -> str:
    try:
        return get_version_from_metadata()
    except metadata.PackageNotFoundError:
        try:
            return get_version_from_pyproject()
        except (FileNotFoundError, KeyError):
            return "unknown"


def show_version() -> None:
    print(get_version())
