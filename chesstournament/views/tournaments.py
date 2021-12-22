# """This module provides the tournaments view."""
# from typing import List
#
# import typer
# from tabulate import tabulate
#
# from chesstournament import __app_name__, ERRORS, DB_WRITE_ERROR
# from chesstournament import config
# from chesstournament.controllers.tournaments import TournamentsManager
# from chesstournament.models.tournament import Tournament, TournamentException
#
# NAME_PROMPT = 'tournament name'
# LOCATION_PROMPT = 'location'
# NB_OF_ROUNDS_PROMPT = 'number of rounds'
# TIME_CONTROL_PROMPT = 'time control (bullet, blitz, rapid)'
# DESCRIPTION_PROMPT = 'description'
#
# TOURNAMENT_COLUMNS = (
# "id", "name", "location", "number_of_rounds", "time_control", "description", "start_date", "end_date")
#
# app = typer.Typer(add_completion=False)
#
#
# @app.command()
# def add():
#     """Add a new tournament to the database."""
#     tournament_fields = _prompt_new_tournament()
#
#     try:
#         tournament = Tournament(*tournament_fields)
#
#         tournaments_manager = get_tournaments_manager()
#         tournaments_manager.add(tournament)
#         typer.secho(
#             f"\nTournament was created successfully.",
#             fg=typer.colors.GREEN,
#         )
#         print_tournaments([tournament])
#     except (TournamentException, Exception) as error:
#         error_message = error.message if isinstance(error, TournamentException) else ERRORS[DB_WRITE_ERROR]
#         typer.secho(
#             f'\nPlayer was not created:\n{error_message}',
#             fg=typer.colors.RED,
#             err=True
#         )
#         raise typer.Exit(1)
#
#
# @app.command("list")
# def list_tournaments():
#     pass
#
#
# def get_tournaments_manager():
#     """Create a TournamentsManager instance."""
#     try:
#         db_path = config.get_database_path()
#         tournaments_manager = TournamentsManager(str(db_path))
#         return tournaments_manager
#     except Exception:
#         typer.secho(
#             f"Config file not found. Please, run '{__app_name__} init'.",
#             fg=typer.colors.RED,
#             err=True
#         )
#         raise typer.Exit(1)
#
#
# def print_tournaments(tournaments: List[Tournament]):
#     """Print a list of tournaments to stdout"""
#     table = []
#     for tournament in tournaments:
#         player_data = []
#         for field in TOURNAMENT_COLUMNS:
#             player_data.append(tournament.get(field))
#         table.append(player_data)
#     typer.echo(f"\n{tabulate(table, TOURNAMENT_COLUMNS, tablefmt='github')}")
#
#
# def _prompt_new_tournament():
#     """Prompts the user to fill in a new tournament's data."""
#     typer.echo("\n[New tournament]\n")
#     name = typer.prompt(NAME_PROMPT)
#     location = typer.prompt(LOCATION_PROMPT)
#     number_of_rounds = typer.prompt(NB_OF_ROUNDS_PROMPT)
#     time_control = typer.prompt(TIME_CONTROL_PROMPT)
#     description = typer.prompt(DESCRIPTION_PROMPT)
#
#     return name, location, number_of_rounds, time_control, description
