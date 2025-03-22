from contextlib import contextmanager
import json
from functools import wraps
from pathlib import Path
from typing import Annotated, Any

import snick
import typer
from inflection import dasherize
from loguru import logger
from pydantic import BaseModel, ValidationError, Field

from drivel.constants import DEFAULT_THEME
from drivel.cli.constants import CACHE_DIR
from drivel.cli.exceptions import Abort, handle_abort
from drivel.cli.cache import init_cache
from drivel.cli.format import terminal_message


settings_path: Path = CACHE_DIR / "settings.json"


def file_exists(value: Path | None) -> Path | None:
    if value is None:
        return value

    value = value.expanduser()
    if not value.exists():
        raise ValueError(f"File not found at {value}")
    return value


class Settings(BaseModel):
    default_theme: str = DEFAULT_THEME

    invalid_warning: Annotated[
        str | None,
        Field(
            exclude=True,
            description="""
            An optional warning that can be included when the model is invalid.

            Used when we use the `attach_settings` decorator with `validate=False`.
        """,
        ),
    ] = None


@contextmanager
def handle_config_error():
    try:
        yield
    except ValidationError as err:
        raise Abort(
            snick.conjoin(
                "A configuration error was detected.",
                "",
                "Details:",
                "",
                f"[red]{err}[/red]",
            ),
            subject="Configuration Error",
            log_message="Configuration error",
        )


def init_settings(validate: bool = True, **settings_values) -> Settings:
    with handle_config_error():
        logger.debug("Validating settings")
        try:
            return Settings(**settings_values)
        except ValidationError as err:
            if validate:
                raise
            settings = Settings.model_construct(**settings_values)
            settings.invalid_warning = str(err)
            return settings


def update_settings(settings: Settings, **settings_values) -> Settings:
    with handle_config_error():
        logger.debug("Validating settings")
        settings_dict = settings.model_dump(exclude_unset=True)
        settings_dict.update(**settings_values)
        return Settings(**settings_dict)


def unset_settings(settings: Settings, *unset_keys) -> Settings:
    with handle_config_error():
        logger.debug("Unsetting settings")
        return Settings(**{k: v for (k, v) in settings.model_dump(exclude_unset=True).items() if k not in unset_keys})


def attach_settings(original_function=None, *, validate=True):
    """
    Attach the settings to the CLI context.

    Optionally, skip validation of the settings. This is useful in case the config
    file being loaded is not valid, but we still want to use the settings. Then, we
    can update the settings with correct values.

    Uses recipe for decorator with optional arguments from:
    https://stackoverflow.com/a/24617244/642511
    """

    def _decorate(func):
        @wraps(func)
        def wrapper(ctx: typer.Context, *args, **kwargs):
            settings_values = {}
            try:
                logger.debug(f"Loading settings from {settings_path}")
                settings_values.update(**json.loads(settings_path.read_text()))
            except FileNotFoundError:
                # If I ever port this into a cli toolkit, need a way to detect if all settings have a default and only
                # trigger this if they do not
                #
                # raise Abort(
                #     f"""
                #     No settings file found at {settings_path}!

                #     Run the bind sub-command first to establish your settings.
                #     """,
                #     subject="Settings file missing!",
                #     log_message="Settings file missing!",
                # )
                pass
            logger.debug("Binding settings to CLI context")
            ctx.obj.settings = init_settings(validate=validate, **settings_values)
            return func(ctx, *args, **kwargs)

        return wrapper

    if original_function:
        return _decorate(original_function)
    else:
        return _decorate


def dump_settings(settings: Settings):
    logger.debug(f"Saving settings to {settings_path}")
    settings_values = settings.model_dump_json(indent=2)
    settings_path.write_text(settings_values)


def clear_settings():
    logger.debug(f"Removing saved settings at {settings_path}")
    settings_path.unlink(missing_ok=True)


def show_settings(settings: Settings):
    parts = []
    for field_name, field_value in settings:
        if field_name == "invalid_warning":
            continue
        parts.append((dasherize(field_name), field_value))
    max_field_len = max(len(field_name) for field_name, _ in parts)
    message = "\n".join(f"[bold]{k:<{max_field_len}}[/bold] -> {v}" for k, v in parts)
    if settings.invalid_warning:
        message += f"\n\n[red]Configuration is invalid: {settings.invalid_warning}[/red]"
    terminal_message(message, subject="Current Configuration")


cli = typer.Typer(help="Configure the app, change settings, or view how it's currently configured")


@cli.command()
@handle_abort
@init_cache
def bind(
    default_theme: Annotated[str, typer.Option(help="The default theme to use in the CLI")],
):
    """
    Bind the configuration to the app.
    """
    logger.debug(f"Initializing settings with {locals()}")
    settings = init_settings(**locals())
    dump_settings(settings)
    show_settings(settings)


@cli.command()
@handle_abort
@init_cache
@attach_settings(validate=False)
def update(
    ctx: typer.Context,
    default_theme: Annotated[str | None, typer.Option(help="The default theme to use in the CLI")],
):
    """
    Update one or more configuration settings that are bound to the app.
    """
    logger.debug(f"Updating settings with {locals()}")
    kwargs: dict[str, Any] = {k: v for (k, v) in locals().items() if v is not None}
    settings = update_settings(ctx.obj.settings, **kwargs)
    dump_settings(settings)
    show_settings(settings)


@cli.command()
@handle_abort
@init_cache
@attach_settings(validate=False)
def unset(
    ctx: typer.Context,
    default_theme: Annotated[bool, typer.Option(help="The default theme to use in the CLI")],
):
    """
    Remove a configuration setting that was previously bound to the app.
    """
    logger.debug(f"Updating settings with {locals()}")
    keys = [k for k in locals() if locals()[k]]
    settings = unset_settings(ctx.obj.settings, *keys)
    dump_settings(settings)
    show_settings(settings)


@cli.command()
@handle_abort
@init_cache
@attach_settings(validate=False)
def show(ctx: typer.Context):
    """
    Show the config that is currently bound to the app.
    """
    show_settings(ctx.obj.settings)


@cli.command()
@handle_abort
@init_cache
def clear():
    """
    Clear the config from the app.
    """
    logger.debug("Clearing settings")
    clear_settings()
