"""CLI general purpose utilities."""

import click
import typer


def print_error(message: str):
    """Prints an error message on stderr."""
    typer.secho(message, fg=typer.colors.RED, err=True)


def print_success(message: str):
    """Prints a success message on stdout."""
    typer.secho(message, fg=typer.colors.GREEN)


def print_raw(message: str):
    """Prints a raw text message on stdout."""
    typer.echo(message)


def prompt_value(description: str, expected_type: type = None) -> any:
    return typer.prompt(f"\n{description}", type=expected_type)


def prompt_menu(menu_items: dict):
    """Prints a menu and prompts the user to make a choice.

    Arguments:
        menu_items -- a dictionary with options as keys and descriptions as values.
    """
    typer.echo()
    for key, value in menu_items.items():
        typer.echo(f"{key}. {value}")

    valid_choices = [str(k) for k in menu_items.keys()]
    choice = typer.prompt("\nChoose an option", type=click.Choice(valid_choices), show_choices=True)
    typer.echo()


    return int(choice) if type(list(menu_items.keys())[0]) == int else choice
