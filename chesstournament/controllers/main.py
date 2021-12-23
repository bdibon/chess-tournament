"""This is the main controller of chesstournament."""

from pathlib import Path
from typing import Optional

import typer

from chesstournament import __app_name__, __version__, config, ERRORS
from chesstournament import cli
from chesstournament.controllers import players, tournaments
from chesstournament.models.database import DEFAULT_DB_LOCATION, DatabaseException, create_database
from chesstournament.models.player import PlayerException, TournamentPlayer
from chesstournament.models.tournament import TournamentException

app = typer.Typer(add_completion=False)
app.add_typer(players.app, name='players', help='Manage players in the app.')
app.add_typer(tournaments.app, name='tournaments', help='Manage tournaments in the app')


class TournamentEngine:
    """This gathers the required functionality by the run tournament command."""

    def __init__(self, tournament, player_manager, tournament_manager):
        self.tournament = tournament
        self.player_manager = player_manager
        self.tournament_manager = tournament_manager

    def populate_competitors(self):
        """Populate competitors with data from the players table."""
        t_players = []
        for lean_player in self.tournament.competitors:
            fat_player = self.player_manager.find(lean_player['id'])
            t_players.append(TournamentPlayer(**fat_player, score=lean_player['score'],
                                              previous_opponents=lean_player['previous_opponents']))
        self.tournament.competitors = t_players

    def add_new_competitor(self):
        player_id, first_name, last_name = cli.tournaments.prompt_new_player()
        new_player = self.player_manager.find(player_id, first_name, last_name)
        if new_player is None:
            cli.utils.print_error("Player not found.")

        t_player = TournamentPlayer.from_player(new_player)
        self.tournament.add_competitor(t_player)
        self.tournament_manager.update_one(self.tournament)

    def display_competitors(self):
        cli.tournaments.print_competitors(self.tournament.name, self.tournament.competitors)


@app.command()
def init(db_path: str = typer.Option(
    str(DEFAULT_DB_LOCATION),
    "--db-path",
    "-db",
    prompt="chesstournament database location?")):
    """Initialize chess tournament local storage."""
    app_init_error = config.init_app(db_path)
    if app_init_error:
        cli.utils.print_error(f"Failed to create config file:\n'{ERRORS[app_init_error]}'")
        raise typer.Exit(1)

    db_init_error = create_database(Path(db_path))
    if db_init_error:
        cli.utils.print_error(f"Failed to create database file:\n'{ERRORS[db_init_error]}'", )
        raise typer.Exit(1)
    else:
        cli.utils.print_success(f"Succeed to create local storage file:\n'{db_path}'")


@app.command()
def run(tournament_id: int = typer.Option(
    ...,
    "--tournament",
    "-t")):
    try:
        tournament_manager = tournaments.get_tournaments_manager()
        player_manager = players.get_players_manager()
        tournament = tournament_manager.get_by_id(tournament_id)
        tournament_engine = TournamentEngine(tournament, player_manager, tournament_manager)

        if tournament.has_competitors():
            tournament_engine.populate_competitors()

        tournament_engine.add_new_competitor()
        tournament_engine.display_competitors()

        # Check if the tournament has started yet.

        # The tournament has not started.
        # List the players participating in the tournament.
        # Ask to add new players (y/n).
        # When the user says no, stop looping and prompt for the first round.
        # The tournament has started.

        # if not tournament.has_started():
        #     while True:
        #         should_add_player = cli.tournaments.should_add_player()
        #         if not should_add_player:
        #             break
        #
        #         player_name = cli.tournaments.prompt_new_player()
        #         new_player = player_manager.get_by_last_name(player_name)
        #         print('hello world')
        #         tournament.add_competitor(new_player)






    except (TournamentException, PlayerException, DatabaseException) as error:
        cli.utils.print_error(f"\nTournament failed:\n{error.message}")
        raise typer.Exit(1)


def version_callback(value: bool):
    if value:
        cli.utils.print_raw(f"{__app_name__} version: {__version__}")
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
