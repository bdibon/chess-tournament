"""This is the main view of chesstournament."""

import typer

def print_error(message: str):
    typer.secho(message, fg=typer.colors.RED, err=True)

def print_success(message: str):
    typer.secho(message, fg=typer.colors.GREEN)

def print_raw(message: str):
    typer.echo(message)