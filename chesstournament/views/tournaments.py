from typing import Tuple

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

ROUND_NAME_PROMPT = 'round name'

ROUND_DETAILS_COLUMNS = (
    "match #", "player 1", "player 2", "outcome",
)

ROUND_OVERVIEW_COLUMNS = (
    "name", "start_date", "end_date", "status"
)

MATCH_HISTORY_COLUMNS = (
    "round", "match #", "player 1", "player 2", "outcome"
)

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


def print_tournaments_overview(tournaments: list):
    """Print a list of tournaments to stdout"""
    table = []
    for tournament in tournaments:
        tournament_data = []
        for field in TOURNAMENT_COLUMNS:
            tournament_data.append(tournament.get(field))
        table.append(tournament_data)
    typer.echo(f"\n{tabulate(table, TOURNAMENT_COLUMNS, tablefmt='github')}\n")

def print_tournament_header(tournament):
    typer.echo(f"[ {tournament.name} - Overview ]")
    print_tournaments_overview([tournament])

def prompt_for_tournament_id() -> int:
    """Prompts the user to fill in a tournament's id."""
    tournament_id = typer.prompt("Tournament id", type=int)
    return tournament_id


def prompt_new_round(tournament_name: str, round_number: int) -> str:
    """Prompts the user to fill in a tournament's round data."""
    typer.echo(f"[ {tournament_name} - New round ]")
    name = typer.prompt('\n' + ROUND_NAME_PROMPT, default=f"Round {round_number}")
    return name


def should_add_player() -> bool:
    """Checks whether the user wants to add a new player or not."""
    should = typer.confirm("Do you want to add a new player?")
    return should


# def prompt_new_player() -> tuple:
#     """Asks user for a new player to add to a tournament."""
#     typer.echo(f"\n[ New player ]\n"
#                f"\n1. Add player from id"
#                f'\n2. Add player from name\n')
#
#     by_id, by_fullname = (1, 2)
#     lookup_method = None
#     while lookup_method not in (by_id, by_fullname):
#         lookup_method = typer.prompt("", prompt_suffix='> ', type=int)
#
#     player_id = None
#     first_name = None
#     last_name = None
#     if lookup_method == by_id:
#         player_id = typer.prompt("\nPlayer's id", type=int)
#     elif lookup_method == by_fullname:
#         first_name = typer.prompt("\nPlayer's first name")
#         last_name = typer.prompt("Player's last name")
#
#     return player_id, first_name, last_name


def print_scoreboard(tournament_name: str, players: list):
    """Print the scoreboard of the tournament."""
    table = []
    for p in players:
        p_data = []
        for field in COMPETITOR_COLUMNS:
            p_data.append(p.get(field))
        table.append(p_data)

    typer.echo(
        f"\n[ {tournament_name} - Scoreboard ]\n"
        f"\n{tabulate(table, COMPETITOR_COLUMNS, tablefmt='github')}\n"
    )


def should_launch():
    should = typer.confirm("Do you want to launch the tournament? (this action is irreversible", default=False)
    typer.echo()
    return should


def print_round_details(round_name: str,
                        round_num: int,
                        total_rounds: int,
                        start_date: str,
                        end_date: str,
                        matches: list):
    """Print a round to stdout"""
    typer.echo(
        f"\n[ {round_name} ({round_num} / {total_rounds}) ]\n"
        f"\nStarted at: {start_date}"
        f"\nEnded at: {end_date or 'N/A'}\n"
    )

    table = []
    for idx, match in enumerate(matches):
        match_data = [f"match {idx + 1}"]

        player1_data, player2_data = match

        player1, score_p1 = player1_data
        player2, score_p2 = player2_data

        fullname_p1 = f'{player1.first_name} {player1.last_name}'
        match_data.append(fullname_p1)
        fullname_p2 = f'{player2.first_name} {player2.last_name}'
        match_data.append(fullname_p2)

        if score_p1 is None:
            outcome = 'N/A'
        elif score_p1 == 1:
            outcome = f'{fullname_p1} wins'
        elif score_p1 == 0.5:
            outcome = 'draw'
        else:
            outcome = f'{fullname_p2} wins'

        match_data.append(outcome)
        table.append(match_data)

    typer.echo(f"\n{tabulate(table, ROUND_DETAILS_COLUMNS, tablefmt='github')}\n")


def print_match(p1_name, p2_name, p1_score, p2_score):
    """Print a match's current state."""
    if p1_score == 0:
        outcome = f"* {p2_name} * wins! (+{p2_score} pts)"
    elif p1_score == 1:
        outcome = f"* {p1_name} * wins! (+{p1_score} pts)"
    elif p1_score == 0.5:
        outcome = f"It's a draw! (+{p1_score} pts each)"
    else:
        outcome = "N/A"

    typer.echo(
        f"\n* {p1_name} * vs * {p2_name} *\n"
        f"Outcome: {outcome}\n"
    )


def print_rounds(tournament_name: str, rounds: list, matches_per_round: int):
    """Print a list of rounds.

    Arguments:
        tournament_name - The name of the parent tournament.
        rounds - A list of dict with the name, start_date, end_date of each round.
        matches_per_round - Number of matches per round.
    """
    table = []
    for r in rounds:
        r_data = []
        for field in ROUND_OVERVIEW_COLUMNS:
            if field == 'status':
                match_id = 0
                while match_id < len(r.matches):
                    match = r.matches[match_id]
                    player1_data, player2_data = match
                    player1, score_p1 = player1_data
                    if score_p1 is None:
                        break
                    match_id += 1
                r_data.append(f"{match_id}/{matches_per_round}")
            else:
                field_data = r.get(field) or "N/A"
                r_data.append(field_data)
        table.append(r_data)

    typer.echo(
        f"\n[ {tournament_name} - Rounds Overview ]\n"
        f"\n{tabulate(table, ROUND_OVERVIEW_COLUMNS, tablefmt='github')}\n"
    )


def print_match_history(headers: tuple, items: list, heading: str = None):
    """Print a match history, that is a list of match with their associated round_name."""

    table = []
    for item in items:
        item_data = []
        for field in headers:
            field_data = item.get(field) or "N/A"
            item_data.append(field_data)
        table.append(item_data)

    content = f"\n{tabulate(table, headers, tablefmt='github')}\n"
    if heading is not None:
        content = f"\n[ {heading} ]\n" + content

    typer.echo(content)