from typing import Annotated, Any

import typer

from drivel.cli.cache import init_cache
from drivel.cli.config import Settings, attach_settings
from drivel.cli.constants import OutputFormat
from drivel.cli.exceptions import handle_abort
from drivel.cli.format import as_spaces, as_lines, as_json
from drivel.themes import Theme


cli = typer.Typer()


@cli.callback(invoke_without_command=True)
@handle_abort
@init_cache
@attach_settings
def give(
    ctx: typer.Context,
    max_count: Annotated[int | None, typer.Argument(help="The maximum number of metasyntactic names to give")] = None,
    do_shuffle: Annotated[bool, typer.Option("--shuffle", help="Mix the names")] = False,
    theme_name: Annotated[
        str | None, typer.Option("--theme", help="The theme to use (If not provided, will use current default")
    ] = None,
    kind: Annotated[str, typer.Option(help="The kind of names to give. Use 'all' to pull from all kinds")] = "default",
    output_format: Annotated[
        OutputFormat, typer.Option("--format", help="The output format to use")
    ] = OutputFormat.spaces,
    fancy: Annotated[bool, typer.Option(help="Enable fancy output")] = True,
    to_clipboard: Annotated[bool, typer.Option(help="Copy output to clipboard")] = True,
):
    """
    Give N fun metasyntactic variable names.
    """
    settings: Settings = ctx.obj.settings
    if theme_name is None:
        theme_name = settings.default_theme
    theme = Theme.load(theme_name)
    items = theme.give(max_count=max_count, kind=kind, do_shuffle=do_shuffle)
    kwargs: dict[str, Any] = dict(
        fancy=fancy,
        to_clipboard=to_clipboard,
    )
    match output_format:
        case OutputFormat.spaces | OutputFormat.lines:
            if fancy:
                kwargs["subject"] = f"Fun names from {theme_name}"
            match output_format:
                case OutputFormat.spaces:
                    as_spaces(items, **kwargs)
                case OutputFormat.lines:
                    as_lines(items, **kwargs)
        case OutputFormat.json:
            as_json(items, **kwargs)
