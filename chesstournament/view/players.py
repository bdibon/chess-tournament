from typing import List

import typer
from tabulate import tabulate

from chesstournament import config, __app_name__
from ..controller.players import PlayersManager
from ..model.player import Player, PlayerException

FIRST_NAME_PROMPT = "first name"
LAST_NAME_PROMPT = "last name"
BIRTH_DATE_PROMPT = "date of birth (YYYY-MM-dd)"
SEX_PROMPT = "sex (M/F)"
ELO_PROMPT = "Elo"

PLAYER_COLUMNS = ("ID", "first_name", "last_name", "birth_date", "sex", "elo")

app = typer.Typer(add_completion=False)


@app.command()
def add():
    """Add a new player to the database."""
    player_fields = _prompt_new_player()

    try:
        player = Player(*player_fields)
        players_manager = get_players_manager()
        players_manager.save(player)
        typer.secho(
            f"\nPlayer was created successfully.",
            fg=typer.colors.GREEN,
        )
        print_players([player])
    except PlayerException as error:
        typer.secho(
            f'\nPlayer was not created:\n{error.message}',
            fg=typer.colors.RED,
            err=True
        )
        raise typer.Exit(1)


def print_players(players: List[Player]):
    """Print a list of players to stdout."""
    table = [[player.id, player.first_name, player.last_name, player.birth_date, player.sex, player.elo] for
             player in players]
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
