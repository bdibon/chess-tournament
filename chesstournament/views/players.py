import typer
from tabulate import tabulate

FIRST_NAME_PROMPT = "first name"
LAST_NAME_PROMPT = "last name"
BIRTH_DATE_PROMPT = "date of birth (YYYY-MM-dd)"
SEX_PROMPT = "sex (M/F)"
ELO_PROMPT = "Elo"

PLAYER_COLUMNS = ("id", "first_name", "last_name", "birth_date", "sex", "elo")

def prompt_new():
    """Prompts the user to fill in a new player's data."""
    typer.echo("\n[New player]\n")
    first_name = typer.prompt(FIRST_NAME_PROMPT)
    last_name = typer.prompt(LAST_NAME_PROMPT)
    birth_date = typer.prompt(BIRTH_DATE_PROMPT)
    sex = typer.prompt(SEX_PROMPT)
    elo = typer.prompt(ELO_PROMPT, type=int)

    return first_name, last_name, birth_date, sex, elo


def print_list(players: list):
    """Print a list of players to stdout."""
    table = []
    for player in players:
        player_data = []
        for field in PLAYER_COLUMNS:
            player_data.append(player.get(field))
        table.append(player_data)
    typer.echo(f"\n{tabulate(table, PLAYER_COLUMNS, tablefmt='github')}")
