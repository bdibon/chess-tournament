from typing import List

import typer
from tabulate import tabulate

from chesstournament import config, __app_name__, ERRORS, DB_READ_ERROR, DB_WRITE_ERROR
from ..controller.players import PlayersManager, PlayerSort, sort_players
from ..model.player import Player, PlayerException

FIRST_NAME_PROMPT = "first name"
LAST_NAME_PROMPT = "last name"
BIRTH_DATE_PROMPT = "date of birth (YYYY-MM-dd)"
SEX_PROMPT = "sex (M/F)"
ELO_PROMPT = "Elo"

PLAYER_COLUMNS = ("id", "first_name", "last_name", "birth_date", "sex", "elo")

app = typer.Typer(add_completion=False)


@app.command()
def add():
    """Add a new player to the database."""
    player_fields = _prompt_new_player()

    try:
        player = Player(*player_fields)
        players_manager = get_players_manager()
        players_manager.add(player)
        typer.secho(
            f"\nPlayer was created successfully.",
            fg=typer.colors.GREEN,
        )
        print_players([player])
    except (PlayerException, Exception) as error:
        error_message = error.message if isinstance(error, PlayerException) else ERRORS[DB_WRITE_ERROR]
        typer.secho(
            f'\nPlayer was not created:\n{error_message}',
            fg=typer.colors.RED,
            err=True
        )
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
        players_manager = get_players_manager()
        saved_players = players_manager.get_all()
        sort_players(saved_players, sort_flag)
        print_players(saved_players)
    except (PlayerException, Exception) as error:
        error_message = error.message if isinstance(error, PlayerException) else ERRORS[DB_READ_ERROR]
        typer.secho(
            f'\nCould not retrieve saved players:\n{error_message}',
            fg=typer.colors.RED,
            err=True
        )
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
        players_manager = get_players_manager()
        player = players_manager.get_by_id(player_id)
        old_elo = player.elo
        player.elo = elo
        players_manager.update_one(player)
        typer.secho(
            f"\nPlayer with id {player_id} ({player.first_name} {player.last_name}) was successfully updated."
            f"\nHis/Her Elo rank went from {old_elo} to {player.elo}.",
            fg=typer.colors.GREEN,
        )
        print_players([player])
    except (PlayerException, Exception) as error:
        error_message = error.message if isinstance(error, PlayerException) else ERRORS[DB_WRITE_ERROR]
        typer.secho(
            f'\nCould not update player with id: {player_id}:\n{error_message}',
            fg=typer.colors.RED,
            err=True
        )
        raise typer.Exit(1)


def print_players(players: List[Player]):
    """Print a list of players to stdout."""
    table = []
    for player in players:
        player_data = []
        for field in PLAYER_COLUMNS:
            player_data.append(player.get(field))
        table.append(player_data)
    typer.echo(f"\n{tabulate(table, PLAYER_COLUMNS, tablefmt='github')}")


def get_players_manager() -> PlayersManager:
    """Create a PlayerManager instance."""
    try:
        db_path = config.get_database_path()
        players_manager = PlayersManager(str(db_path))
        return players_manager
    except Exception:
        typer.secho(
            f"Config file not found. Please, run '{__app_name__} init'.",
            fg=typer.colors.RED,
            err=True
        )
        raise typer.Exit(1)


def _prompt_new_player():
    """Prompts the user to fill in a new player's data."""
    typer.echo("\n[New player]\n")
    first_name = typer.prompt(FIRST_NAME_PROMPT)
    last_name = typer.prompt(LAST_NAME_PROMPT)
    birth_date = typer.prompt(BIRTH_DATE_PROMPT)
    sex = typer.prompt(SEX_PROMPT)
    elo = typer.prompt(ELO_PROMPT, type=int)

    return first_name, last_name, birth_date, sex, elo
