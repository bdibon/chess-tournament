"""This module handles the operations with the database."""

from pathlib import Path

from tinydb import TinyDB

from chesstournament import DB_WRITE_ERROR

DEFAULT_DB_LOCATION = Path.home() / '.chess_tournament.json'

def create_database(db_path: Path = DEFAULT_DB_LOCATION):
    try:
        TinyDB(Path.home() / 'sblurp' / 'did_it_work.json')
    except OSError:
        return DB_WRITE_ERROR

create_database()
# print(DEFAULT_DB_LOCATION)
# db = TinyDB('db.json')
# db.truncate()
# # db.insert({'first_name': 'Boris', 'last_name': 'Dibon'})
# table = db.table('players')
# table.insert({'first_name': 'Boris', 'last_name': 'Dibon'})
# print(table.all())