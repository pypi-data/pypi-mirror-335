import snick
import typer

from drivel.cli.config import cli as config_cli
from drivel.cli.format import terminal_message
from drivel.cli.give import cli as give_cli
from drivel.cli.logging import init_logs
from drivel.cli.schemas import CliContext
from drivel.cli.themes import cli as themes_cli
from drivel.cli.version import show_version


cli = typer.Typer(rich_markup_mode="rich")


@cli.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, help="Enable verbose logging to the terminal"),
    version: bool = typer.Option(False, help="Print the version of this app and exit"),
):
    """
    Welcome to meta-fun!

    More information can be shown for each command listed below by running it with the
    --help option.
    """

    if version:
        show_version()
        ctx.exit()

    if ctx.invoked_subcommand is None:
        terminal_message(
            snick.conjoin(
                "No command provided. Please check [bold magenta]usage[/bold magenta]",
                "",
                f"[yellow]{ctx.get_help()}[/yellow]",
            ),
            subject="Need an Armasec command",
        )
        ctx.exit()

    init_logs(verbose=verbose)
    ctx.obj = CliContext()


cli.add_typer(config_cli, name="config")
cli.add_typer(give_cli, name="give")
cli.add_typer(themes_cli, name="themes")


if __name__ == "__main__":
    cli()
