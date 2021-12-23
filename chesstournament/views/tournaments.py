import typer
from tabulate import tabulate

TOURNAMENT_NAME_PROMPT = 'tournament name'
TOURNAMENT_LOCATION_PROMPT = 'location'
TOURNAMENT_NB_OF_ROUNDS_PROMPT = 'number of rounds'
TOURNAMENT_TIME_CONTROL_PROMPT = 'time control (bullet, blitz, rapid)'
TOURNAMENT_DESCRIPTION_PROMPT = 'description'
TOURNAMENT_START_DATE_PROMPT = "Start date (YYYY-MM-DD)"
TOURNAMENT_END_DATE_PROMPT = "End date (YYYY-MM-DD)"

TOURNAMENT_COLUMNS = (
    "id", "name", "location", "number_of_rounds", "time_control", "description", "start_date", "end_date")

COMPETITOR_COLUMNS = (
    "id", "first_name", "last_name", "elo", 'score'
)

ROUND_NAME = 'round name'

def prompt_new() -> dict:
    """Prompts the user to fill in a new tournament's data."""
    typer.echo("\n[ New tournament ]\n")

    name = typer.prompt(TOURNAMENT_NAME_PROMPT)
    location = typer.prompt(TOURNAMENT_LOCATION_PROMPT)
    number_of_rounds = typer.prompt(TOURNAMENT_NB_OF_ROUNDS_PROMPT)
    time_control = typer.prompt(TOURNAMENT_TIME_CONTROL_PROMPT)
    description = typer.prompt(TOURNAMENT_DESCRIPTION_PROMPT)
    start_date = typer.prompt(TOURNAMENT_START_DATE_PROMPT)
    end_date = typer.prompt(TOURNAMENT_END_DATE_PROMPT)

    return dict(zip(TOURNAMENT_COLUMNS[1:],
                    (name, location, number_of_rounds, time_control, description, start_date, end_date)))


def print_list(tournaments: list):
    """Print a list of tournaments to stdout"""
    table = []
    for tournament in tournaments:
        tournament_data = []
        for field in TOURNAMENT_COLUMNS:
            tournament_data.append(tournament.get(field))
        table.append(tournament_data)
    typer.echo(f"\n{tabulate(table, TOURNAMENT_COLUMNS, tablefmt='github')}\n")


def prompt_for_tournament_id() -> int:
    """Prompts the user to fill in a tournament's id."""
    tournament_id = typer.prompt("Tournament id", type=int)
    return tournament_id


def prompt_new_round(round_number) -> str:
    """Prompts the user to fill in a tournament's round data."""
    name = typer.prompt('\n' + ROUND_NAME, default=f"Round {round_number}")
    return name


def should_add_player() -> bool:
    """Checks whether the user wants to add a new player or not."""
    should = typer.confirm("Do you want to add a new player?")
    return should

def prompt_new_player() -> tuple:
    """Asks user for a new player to add to a tournament."""
    typer.echo(f"\n[ New player ]\n"
               f"\n1. Add player from id"
               f'\n2. Add player from name\n')

    by_id, by_fullname = (1, 2)
    lookup_method = None
    while lookup_method not in (by_id, by_fullname):
        lookup_method = typer.prompt("", prompt_suffix='> ', type=int)

    player_id = None
    first_name = None
    last_name = None
    if lookup_method == by_id:
        player_id = typer.prompt("\nPlayer's id", type=int)
    elif lookup_method == by_fullname:
        first_name = typer.prompt("\nPlayer's first name")
        last_name = typer.prompt("Player's last name")

    return player_id, first_name, last_name

def print_competitors(tournament_name: str, players: list):
    """Print a list of competitors to stdout"""
    table = []
    for p in players:
        p_data = []
        for field in COMPETITOR_COLUMNS:
            p_data.append(p.get(field))
        table.append(p_data)

    typer.echo(
        f"\n[ List of {tournament_name} competitors ]\n"
        f"\n{tabulate(table, COMPETITOR_COLUMNS, tablefmt='github')}\n"
    )