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

ROUND_OVERVIEW_COLUMNS = (
    "name", "start_date", "end_date", "status"
)


class TournamentCLIView:
    @staticmethod
    def prompt_for_new_tournament() -> dict:
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

    @staticmethod
    def print_tournaments(tournaments: list):
        """Print a list of tournaments to stdout"""
        table = []
        for tournament in tournaments:
            tournament_data = []
            for field in TOURNAMENT_COLUMNS:
                tournament_data.append(tournament.get(field))
            table.append(tournament_data)
        typer.echo(f"\n{tabulate(table, TOURNAMENT_COLUMNS, tablefmt='github')}\n")

    @staticmethod
    def print_match(p1_name: str, p2_name: str, p1_score: int, p2_score: int):
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

    @staticmethod
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
