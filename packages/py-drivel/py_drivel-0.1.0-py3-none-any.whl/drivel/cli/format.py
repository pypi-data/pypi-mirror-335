import json
from typing import Any, Iterable

import pyperclip
import snick
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown


def _to_clipboard(text) -> bool:
    try:
        pyperclip.copy(text)
        return True
    except Exception as exc:
        logger.debug(f"Could not copy letter to clipboard: {exc}")
        return False


def terminal_message(
    message,
    subject=None,
    color="green",
    footer=None,
    indent=True,
    markdown=False,
    to_clipboard=False,
):
    if to_clipboard:
        result = _to_clipboard(message)
        if result and not footer:
            footer = "Copied to clipboard!"
    panel_kwargs: dict[str, Any] = dict(padding=1)
    if subject is not None:
        panel_kwargs["title"] = f"[{color}]{subject}"
    if footer is not None:
        panel_kwargs["subtitle"] = f"[dim italic]{footer}[/dim italic]"
    text = snick.dedent(message)
    if indent:
        text = snick.indent(text, prefix="  ")
    if markdown:
        text = Markdown(text)
    console = Console()
    console.print()
    console.print(Panel(text, **panel_kwargs))
    console.print()


def simple_message(
    message,
    indent=False,
    markdown=False,
    to_clipboard=False,
):
    text = snick.dedent(message)
    if indent:
        text = snick.indent(text, prefix="  ")
    if markdown:
        text = Markdown(text)
    if to_clipboard:
        result = _to_clipboard(text)
        if result:
            logger.debug("output copied to clipboard")
    console = Console()
    console.print()
    console.print(text)
    console.print()


def as_spaces(stuff: Iterable, fancy: bool = False, **kwargs):
    output = " ".join(stuff)
    if fancy:
        return terminal_message(output, **kwargs)
    else:
        kwargs.pop("subject", None)
    return simple_message(output, **kwargs)


def as_lines(stuff: Iterable, fancy: bool = False, **kwargs):
    output = "\n".join(stuff)
    if fancy:
        return terminal_message(output, **kwargs)
    else:
        kwargs.pop("fancy", None)
    return simple_message(output, **kwargs)


def as_json(stuff, fancy: bool = False, to_clipboard=False, **kwargs):
    indent: int | None = 2 if fancy else None
    if to_clipboard:
        result = _to_clipboard(json.dumps(stuff, indent=indent))
        if result:
            logger.debug("output copied to clipboard")
    console = Console()
    console.print()
    console.print_json(data=stuff, indent=indent, **kwargs)
    console.print()
