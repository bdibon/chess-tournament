"""This is the chess-tournament CLI."""

from pathlib import Path
from typing import Optional

import typer

from chesstournament import __app_name__, __version__, config, ERRORS
from ..model import database
from ..view import players

app = typer.Typer(add_completion=False)
app.add_typer(players.app, name='players')

@app.command()
def init(db_path: str = typer.Option(
    str(database.DEFAULT_DB_LOCATION),
    "--db-path",
    "-db",
    prompt="chesstournament database location?")):
    """Initialize chess tournament local storage."""
    app_init_error = config.init_app(db_path)
    if app_init_error:
        typer.secho(
            f"Failed to create config file with '{ERRORS[app_init_error]}'",
            fg=typer.colors.RED
        )
        raise typer.Exit(1)

    db_init_error = database.create_database(Path(db_path))
    if db_init_error:
        typer.secho(
            f"Failed to create database file with '{ERRORS[db_init_error]}'",
            fg=typer.colors.RED
        )
        raise typer.Exit(1)
    else:
        typer.secho(
            f"Succeed to create local storage file: '{db_path}'",
            fg=typer.colors.GREEN
        )

def version_callback(value: bool):
    if value:
        typer.echo(f"{__app_name__} version: {__version__}")
        raise typer.Exit()
    return None


@app.callback()
def main(
        verbose: Optional[bool] = typer.Option(
            None,
            "--version",
            "-v",
            help="Show the application's version and exit.",
            callback=version_callback,
            is_eager=True
        )):
    """
    A CLI app to manage chess tournaments.
    """
    return None
