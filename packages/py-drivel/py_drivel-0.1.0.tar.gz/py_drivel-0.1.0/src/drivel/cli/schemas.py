from dataclasses import dataclass

from drivel.cli.config import Settings


@dataclass
class CliContext:
    settings: Settings | None = None
