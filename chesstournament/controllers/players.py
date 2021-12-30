"""This module defines the controller to manage players."""

from enum import Flag, auto
from operator import attrgetter
from typing import List

import typer

from chesstournament import view, config, __app_name__
from chesstournament.models.database import PlayersRegistry, DatabaseException
from chesstournament.models.player import Player, PlayerException

app = typer.Typer(add_completion=False)


@app.command()
def add():
    """Add a new player to the database."""
    try:
        player_fields = view.prompt_for_new_player()
        player = Player(**player_fields)

        players_registry = get_players_registry()
        players_registry.add(player)

        view.print_success("\nPlayer was created successfully.")
        view.print_players([player])
    except (PlayerException, DatabaseException) as error:
        view.print_error(f'\nPlayer was not created:\n{error.message}')
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

    try:
        players_registry = get_players_registry()

        saved_players = players_registry.get_all()
        sort_players(saved_players, sort_flag)
        view.print_players(saved_players)
    except (PlayerException, DatabaseException) as error:
        view.print_error(f'\nCould not retrieve saved players:\n{error.message}')
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
    try:
        players_registry = get_players_registry()
        player = players_registry.find(player_id)

        if player is None:
            view.print_error("Player not found.")
            raise typer.Exit(1)

        old_elo = player.elo
        player.elo = elo
        players_registry.update_one(player)
        view.print_success(
            f"\nPlayer with id {player_id} ({player.first_name} {player.last_name}) was successfully updated."
            f"\nHis/Her Elo rank went from {old_elo} to {player.elo}.")
        view.print_players([player])
    except (PlayerException, DatabaseException) as error:
        view.print_error(f'\nCould not update player with id: {player_id}:\n{error.message}')
        raise typer.Exit(1)


def get_players_registry() -> PlayersRegistry:
    """Create a PlayerRegistry instance."""
    try:
        db_path = config.get_database_path()
        players_registry = PlayersRegistry(str(db_path))
        return players_registry
    except Exception:
        view.print_error(f"Config file not found. Please, run '{__app_name__} init'.")
        raise typer.Exit(1)


class PlayerSort(Flag):
    """Sorting flags for players"""
    NONE = 0
    ALPHA = auto()
    ELO = auto()


def sort_players(players: List[Player], flag: PlayerSort = PlayerSort.NONE) -> None:
    """Sort players according to the specified flag. Many flags results in undefined behavior."""
    if flag == PlayerSort.NONE:
        return None
    if flag == PlayerSort.ALPHA:
        players.sort(key=attrgetter('last_name', 'first_name'))
    if flag == PlayerSort.ELO:
        players.sort(key=attrgetter('elo'), reverse=True)
