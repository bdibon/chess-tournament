"""This module handles the operations with the database."""

from pathlib import Path

from tinydb import TinyDB

from chesstournament import DB_WRITE_ERROR, SUCCESS

DEFAULT_DB_LOCATION = Path.home() / '.chess_tournament.json'

def create_database(db_path: Path = DEFAULT_DB_LOCATION) -> int:
    """Creates a local database file at 'db_path'."""
    try:
        TinyDB(db_path)
    except OSError:
        return DB_WRITE_ERROR

    return SUCCESS
