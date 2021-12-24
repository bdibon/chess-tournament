"""This module provides the tournaments view."""

from datetime import datetime, MAXYEAR
from enum import Flag, auto
from typing import List

import typer

from chesstournament import cli, __app_name__
from chesstournament import config
from chesstournament.models.database import TournamentsRegistry, DatabaseException
from chesstournament.models.tournament import Tournament, TournamentException, TIME_FORMAT_TOURNAMENT

app = typer.Typer(add_completion=False)


@app.command()
def add():
    """Add a new tournament to the database."""
    tournament_fields = cli.tournaments.prompt_new()

    try:
        tournament = Tournament(**tournament_fields)

        tournaments_manager = get_tournaments_registry()
        tournaments_manager.add(tournament)
        cli.utils.print_success(f"\nTournament was created successfully.")
        cli.tournaments.print_list([tournament])
    except (TournamentException, DatabaseException) as error:
        cli.utils.print_error(f'\nTournament was not created:\n{error.message}')
        raise typer.Exit(1)


@app.command("list")
def list_tournaments(
        sort_recent: bool = typer.Option(
            False,
            "--sort-recent",
            help="Sort the tournaments by date (recent first)"
        ),
):
    """List saved tournaments, sorted by id (default).

    Combining different sorting options has undefined behavior.
    """
    sort_flag = TournamentSort.NONE
    if sort_recent:
        sort_flag |= TournamentSort.RECENT

    tournament_registry = get_tournaments_registry()

    try:
        saved_tournaments = tournament_registry.get_all()
        sort_tournaments(saved_tournaments, sort_flag)
        cli.tournaments.print_list(saved_tournaments)
    except (TournamentException, DatabaseException) as error:
        cli.utils.print_error(f'\nCould not retrieve saved players:\n{error.message}')
        raise typer.Exit(1)


def get_tournaments_registry():
    """Create a TournamentsRegistry instance."""
    try:
        db_path = config.get_database_path()
        tournaments_registry = TournamentsRegistry(str(db_path))
        return tournaments_registry
    except Exception:
        cli.utils.print_error(f"Config file not found. Please, run '{__app_name__} init'.")
        raise typer.Exit(1)


class TournamentSort(Flag):
    NONE = 0
    RECENT = auto()


def sort_tournaments(tournaments: List[Tournament], flag: TournamentSort = TournamentSort.NONE) -> None:
    """Sort tournaments according to the specified flag. Many flags results in undefined behavior."""

    def _sort_recent(tournament: Tournament) -> datetime:
        # 'None' start_date matches current or future tournaments.
        try:
            start_date = datetime.strptime(tournament.start_date, TIME_FORMAT_TOURNAMENT)
        except TypeError:
            start_date = datetime(year=MAXYEAR, month=1, day=1)
        return start_date

    if flag == TournamentSort.NONE:
        return None
    if flag == TournamentSort.RECENT:
        tournaments.sort(key=_sort_recent, reverse=True)
