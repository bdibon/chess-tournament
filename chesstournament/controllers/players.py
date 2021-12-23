"""This module defines the controller to manage players."""

from enum import Flag, auto
from typing import List

import typer

from chesstournament import cli, config, __app_name__
from chesstournament.models.database import PlayersManager, DatabaseException
from chesstournament.models.player import Player, PlayerException

app = typer.Typer(add_completion=False)


@app.command()
def add():
    """Add a new player to the database."""
    player_fields = cli.players.prompt_new()

    try:
        player = Player(*player_fields)

        players_manager = get_players_manager()
        players_manager.add(player)

        cli.utils.print_success(f"\nPlayer was created successfully.")
        cli.players.print_list([player])
    except (PlayerException, DatabaseException) as error:
        cli.utils.print_error(f'\nPlayer was not created:\n{error.message}')
        raise typer.Exit(1)


@app.command("list")
def list_players(
        sort_alpha: bool = typer.Option(
            False,
            "--sort-alpha",
            help="Sort the players alphabetically by their last name."
        ),
        sort_elo: bool = typer.Option(
            False,
            "--sort-elo",
            help="Sort the players by their Elo rank."
        )
):
    """List saved players, sorted by id (default).

    Combining different sorting options has undefined behavior.
    """
    sort_flag = PlayerSort.NONE
    if sort_alpha:
        sort_flag |= PlayerSort.ALPHA
    if sort_elo:
        sort_flag |= PlayerSort.ELO

    players_manager = get_players_manager()

    try:
        saved_players = players_manager.get_all()
        sort_players(saved_players, sort_flag)
        cli.players.print_list(saved_players)
    except (PlayerException, DatabaseException) as error:
        cli.utils.print_error(f'\nCould not retrieve saved players:\n{error.message}')
        raise typer.Exit(1)


@app.command()
def update(
        player_id: int = typer.Option(
            ...,
            "--id",
            help="The 'id' of the player to update."
        ),
        elo: int = typer.Option(
            ...,
            help="The new Elo rating of the player."
        )):
    """Update a player in the local database."""
    players_manager = get_players_manager()

    try:
        player = players_manager.find(player_id)

        if player is None:
            cli.utils.print_error("Player not found.")
            raise typer.Exit(1)

        old_elo = player.elo
        player.elo = elo
        players_manager.update_one(player)
        cli.utils.print_success(
            f"\nPlayer with id {player_id} ({player.first_name} {player.last_name}) was successfully updated."
            f"\nHis/Her Elo rank went from {old_elo} to {player.elo}.")
        cli.players.print_list([player])
    except (PlayerException, DatabaseException) as error:
        cli.utils.print_error(f'\nCould not update player with id: {player_id}:\n{error.message}')
        raise typer.Exit(1)


def get_players_manager() -> PlayersManager:
    """Create a PlayerManager instance."""
    try:
        db_path = config.get_database_path()
        players_manager = PlayersManager(str(db_path))
        return players_manager
    except Exception:
        cli.utils.print_error(f"Config file not found. Please, run '{__app_name__} init'.")
        raise typer.Exit(1)


class PlayerSort(Flag):
    """Sorting flags for players"""
    NONE = 0
    ALPHA = auto()
    ELO = auto()


def sort_players(players: List[Player], flag: PlayerSort = PlayerSort.NONE) -> None:
    """Sort players according to the specified flag. Many flags results in undefined behavior."""

    def _sort_alpha(player):
        return player.last_name

    def _sort_elo(player):
        return player.elo

    if flag == PlayerSort.NONE:
        return None
    if flag == PlayerSort.ALPHA:
        players.sort(key=_sort_alpha)
    if flag == PlayerSort.ELO:
        players.sort(key=_sort_elo, reverse=True)
