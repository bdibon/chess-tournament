"""CLI general purpose utilities."""

import click
import typer
from tabulate import tabulate

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
    menu_keys = sorted(menu_items.keys())
    for key in menu_keys:
        typer.echo(f"{key}. {menu_items[key]}")

    valid_choices = [str(k) for k in menu_items.keys()]
    choice = typer.prompt("\nChoose an option", type=click.Choice(valid_choices), show_choices=True)
    typer.echo()


    return int(choice) if type(list(menu_items.keys())[0]) == int else choice


def print_tabular_data(header: tuple, items: list, heading: str = None, description: str = None):
    """Print tabular items data with its associated header, eventually with heading and description."""
    table = []
    for item in items:
        item_data = []
        for field in header:
            field_data = item.get(field) or "N/A"
            item_data.append(field_data)
        table.append(item_data)

    content = f"\n{tabulate(table, header, tablefmt='github')}\n"
    if heading is not None:
        content = f"\n[ {heading} ]\n" + content

    typer.echo(content)