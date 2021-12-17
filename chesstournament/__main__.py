"""The entry point for chesstournament."""

from chesstournament.view.cli import app

# def main(name: str, last_name: str = "", formal: bool = False):
#     """
#     Say hi to NAME, optionally with a --lastname.
#
#     If --formal is used, say hi very formally.
#     """
#     if formal:
#         typer.echo(f"Greetings dear {name} {last_name}")
#     else:
#         typer.echo(f'Hello {name} {last_name}')

if __name__ == '__main__':
    app()
