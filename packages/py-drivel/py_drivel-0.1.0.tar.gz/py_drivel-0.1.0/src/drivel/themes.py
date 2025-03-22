import re
from pathlib import Path
from random import shuffle
from typing import Generator

from auto_name_enum import AutoNameEnum, auto
from loguru import logger
import strictyaml
from pydantic import BaseModel, model_validator

from drivel.constants import DEFAULT_THEME
from drivel.exceptions import DrivelException
from drivel.utilities import asset_root


Kinds = dict[str, list[str]]
kind_pattern = r"^[a-z0-9-]+$"


class Display(AutoNameEnum):
    kebab = auto()
    snake = auto()
    title = auto()
    upper = auto()


class ThemeMetadata(BaseModel):
    attribution: str | None = None
    explanation: str | None = None


class Theme(BaseModel):
    name: str
    default: str
    kinds: Kinds
    metadata: ThemeMetadata

    @model_validator(mode="after")
    def validate_theme(self) -> "Theme":
        if self.default not in self.kinds:
            raise ValueError("Default kind not found in kinds")
        for kind, items in self.kinds.items():
            if not re.match(kind_pattern, kind):
                raise ValueError(f"Kind name '{kind}' has invalid characters")
            if not items:
                raise ValueError(f"Kind '{kind}' has no items")
            for item in items:
                if not re.match(kind_pattern, item):
                    raise ValueError(f"Item '{item}' in kind '{kind}' has invalid characters")
        return self

    def give(
        self,
        max_count: int | None = None,
        kind: str = "default",
        do_shuffle: bool = False,
    ) -> list[str]:
        logger.debug(f"Giving items from {self.name} for kind '{kind}'")
        if kind == "all":
            items = [i for k in self.kinds.values() for i in k]
        else:
            items = self.kinds[self.default]
        if do_shuffle:
            shuffle(items)
        if max_count is None:
            return items
        return items[:max_count]

    @classmethod
    def load(cls, name: str = DEFAULT_THEME) -> "Theme":
        theme_path = asset_root / f"{name}.yaml"
        with DrivelException.handle_errors(f"Theme '{name}' not found"):
            text = theme_path.read_text()
        data = strictyaml.load(text).data
        return Theme(name=name, **data)

    @classmethod
    def names(cls) -> Generator[str, None, None]:
        for asset in asset_root.iterdir():
            if not asset.is_file:
                continue
            filename = Path(asset.name)
            if filename.suffix != ".yaml":
                continue
            yield filename.stem
