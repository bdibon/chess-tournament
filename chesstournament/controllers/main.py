"""This is the main controller of chesstournament."""

from pathlib import Path
from typing import Optional
import itertools

import typer

from chesstournament import __app_name__, __version__, config, ERRORS
from chesstournament import cli
from chesstournament.controllers import players, tournaments
from chesstournament.controllers.players import PlayerSort, sort_players
from chesstournament.models.database import DEFAULT_DB_LOCATION, DatabaseException, create_database
from chesstournament.models.player import PlayerException, TournamentPlayer
from chesstournament.models.tournament import TournamentException

app = typer.Typer(add_completion=False)
app.add_typer(players.app, name='players', help='Manage players in the app.')
app.add_typer(tournaments.app, name='tournaments', help='Manage tournaments in the app')


class TournamentEngine:
    """This gathers the required functionality by the run tournament command."""

    def __init__(self, tournament, player_manager, tournament_registry):
        self.tournament = tournament
        self.player_manager = player_manager
        self.tournament_registry = tournament_registry

    def has_populated_competitors(self) -> bool:
        """Checks whether it should populate competitors or not."""
        return self.tournament.has_competitors() and isinstance(self.tournament.competitors[0], TournamentPlayer)

    def populate_competitors(self) -> None:
        """Populate competitors with data from the players table."""
        t_players = []
        for lean_player in self.tournament.competitors:
            fat_player = self.player_manager.find(lean_player['id'])
            t_players.append(TournamentPlayer(**fat_player, score=lean_player['score'],
                                              previous_opponents=lean_player['previous_opponents']))
        self.tournament.competitors = t_players

    def add_new_competitor(self) -> None:
        """Prompts the user to add a competitor, add it to the current tournament and save it."""
        player_id, first_name, last_name = cli.tournaments.prompt_new_player()
        new_player = self.player_manager.find(player_id, first_name, last_name)
        if new_player is None:
            cli.utils.print_error("Player not found.")

        t_player = TournamentPlayer.from_player(new_player)
        self.tournament.add_competitor(t_player)
        self.tournament_registry.update_one(self.tournament)

    def has_populated_rounds(self) -> bool:
        """Checks whether it should populate rounds or not."""
        if not self.tournament.has_started():
            return True

        first_round = self.tournament.rounds[0]
        sample_data = first_round[0]
        sample_player = sample_data[0]

        return isinstance(sample_player, TournamentPlayer)

    def populate_rounds(self) -> None:
        """Populate rounds with data from the tournament's competitors."""
        if not self.has_populated_competitors():
            self.populate_competitors()

        for lean_round in self.tournament.rounds:
            p1_id = lean_round[0][0]
            p2_id = lean_round[1][0]

            tp1, = (tp for tp in self.tournament.competitors if tp.id == p1_id)
            tp2, = (tp for tp in self.tournament.competitors if tp.id == p2_id)

            lean_round[0][0] = tp1
            lean_round[1][0] = tp2

    def display_competitors(self):
        """Display competitors of the current tournament."""
        cli.tournaments.print_competitors(self.tournament.name, self.tournament.competitors)

    def display_tournament(self):
        """Display basic info about the current tournament."""
        cli.tournaments.print_list([self.tournament])

    def launch(self) -> None:
        """Creates the first round of the tournament."""
        # Sort players by elo.
        sort_players(self.tournament.competitors, PlayerSort.ELO)
        cli.players.print_list(self.tournament.competitors)

        # Split the resulting list in half.
        middle_idx = len(self.tournament.competitors) // 2
        top_players = self.tournament.competitors[:middle_idx]
        bot_players = self.tournament.competitors[middle_idx:]

        # Make pairs with players of each list.
        matches = list(itertools.zip_longest(top_players, bot_players))

        # Add first round to the tournament.
        round_name = cli.tournaments.prompt_new_round(len(self.tournament.rounds) + 1)
        self.tournament.add_round(round_name, matches)
        self.tournament_registry.update_one(self.tournament)

        cli.tournaments.print_round(self.tournament.rounds[0])
        typer.Exit(0)

    def _prepare_first_round(self):
        pass

    def resume(self) -> None:
        if not self.has_populated_competitors():
            self.populate_competitors()
        if not self.has_populated_rounds():
            self.populate_rounds()


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
    "-t",
    help="A tournament id.")):
    """Run an existing tournament interactively."""
    try:
        tournament_registry = tournaments.get_tournaments_registry()
        player_manager = players.get_players_registry()
        tournament = tournament_registry.get_by_id(tournament_id)
        tournament_engine = TournamentEngine(tournament, player_manager, tournament_registry)
        tournament_engine.display_tournament()

        if tournament.has_competitors():
            tournament_engine.populate_competitors()

        if tournament.has_started():
            tournament_engine.resume()


        while True:
            tournament_engine.display_competitors()
            if tournament.has_enough_competitors():
                should_launch = cli.tournaments.should_launch()
                if should_launch:
                    tournament_engine.launch()
                    break

            tournament_engine.add_new_competitor()

    except (TournamentException, PlayerException, DatabaseException) as error:
        cli.utils.print_error(f"\nTournament execution failed:\n{error.message}")
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
