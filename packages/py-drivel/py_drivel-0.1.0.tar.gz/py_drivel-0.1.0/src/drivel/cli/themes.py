from typing import Annotated

import typer

from drivel.cli.cache import init_cache
from drivel.cli.config import attach_settings
from drivel.cli.constants import OutputFormat
from drivel.cli.exceptions import handle_abort
from drivel.cli.format import as_spaces, as_lines, as_json
from drivel.themes import Theme


cli = typer.Typer()


@cli.callback(invoke_without_command=True)
@handle_abort
@init_cache
@attach_settings
def themes(
    ctx: typer.Context,
    output_format: Annotated[
        OutputFormat, typer.Option("--format", help="The output format to use")
    ] = OutputFormat.spaces,
    fancy: Annotated[bool, typer.Option(help="Enable fancy output")] = True,
    to_clipboard: Annotated[bool, typer.Option(help="Copy output to clipboard")] = True,
):
    """
    Fetch all available themes.
    """
    theme_list = list(Theme.names())
    match output_format:
        case OutputFormat.spaces:
            as_spaces(theme_list, fancy=fancy, to_clipboard=to_clipboard)
        case OutputFormat.lines:
            as_lines(theme_list, fancy=fancy, to_clipboard=to_clipboard)
        case OutputFormat.json:
            as_json(theme_list, fancy=fancy, to_clipboard=to_clipboard)


# Include a command to show metadata for a theme
