import typer
from tabulate import tabulate

NAME_PROMPT = 'tournament name'
LOCATION_PROMPT = 'location'
NB_OF_ROUNDS_PROMPT = 'number of rounds'
TIME_CONTROL_PROMPT = 'time control (bullet, blitz, rapid)'
DESCRIPTION_PROMPT = 'description'
START_DATE_PROMPT = "Start date (YYYY-MM-DD)"
END_DATE_PROMPT = "End date (YYYY-MM-DD)"

TOURNAMENT_COLUMNS = (
    "id", "name", "location", "number_of_rounds", "time_control", "description", "start_date", "end_date")


def prompt_new():
    """Prompts the user to fill in a new tournament's data."""
    typer.echo("\n[New tournament]\n")

    name = typer.prompt(NAME_PROMPT)
    location = typer.prompt(LOCATION_PROMPT)
    number_of_rounds = typer.prompt(NB_OF_ROUNDS_PROMPT)
    time_control = typer.prompt(TIME_CONTROL_PROMPT)
    description = typer.prompt(DESCRIPTION_PROMPT)
    start_date = typer.prompt(START_DATE_PROMPT)
    end_date = typer.prompt(END_DATE_PROMPT)

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
    typer.echo(f"\n{tabulate(table, TOURNAMENT_COLUMNS, tablefmt='github')}")
