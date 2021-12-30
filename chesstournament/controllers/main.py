"""This is the main controller of chesstournament."""

from pathlib import Path
from typing import Optional

import typer

from chesstournament import __app_name__, __version__, config, ERRORS, view
from chesstournament.controllers import players, tournaments
from chesstournament.controllers.tournament_engine import TournamentEngine, TournamentEngineException
from chesstournament.models.database import DEFAULT_DB_LOCATION, DatabaseException, create_database
from chesstournament.models.player import PlayerException
from chesstournament.models.tournament import TournamentException

app = typer.Typer(add_completion=False)
app.add_typer(players.app, name='players', help='Manage players in the app.')
app.add_typer(tournaments.app, name='tournaments', help='Manage tournaments in the app')


@app.command()
def init(db_path: str = typer.Option(
        str(DEFAULT_DB_LOCATION),
        "--db-path",
        "-db",
        prompt="chesstournament database location?")):
    """Initialize chess tournament local storage."""
    app_init_error = config.init_app(db_path)
    if app_init_error:
        view.print_error(f"Failed to create config file:\n'{ERRORS[app_init_error]}'")
        raise typer.Exit(1)

    db_init_error = create_database(Path(db_path))
    if db_init_error:
        view.print_error(f"Failed to create database file:\n'{ERRORS[db_init_error]}'", )
        raise typer.Exit(1)
    else:
        view.print_success(f"Succeed to create local storage file:\n'{db_path}'")


@app.command()
def run(tournament_id: int = typer.Option(
        ...,
        "--tournament",
        "-t",
        help="A tournament id.")):
    """Run an existing tournament interactively."""
    try:
        tournament_registry = tournaments.get_tournaments_registry()
        players_registry = players.get_players_registry()
        tournament = tournament_registry.get_by_id(tournament_id)
        tournament_engine = TournamentEngine(tournament, players_registry, tournament_registry)

        if tournament.has_started:
            tournament_engine.resume()
        else:
            tournament_engine.prepare()

    except (TournamentException, PlayerException, DatabaseException, TournamentEngineException) as error:
        view.print_error(f"\nTournament execution failed:\n{error.message}")
        raise typer.Exit(1)


def version_callback(value: bool):
    if value:
        view.print_raw(f"{__app_name__} version: {__version__}")
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
