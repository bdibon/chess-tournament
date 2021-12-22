"""This module handles the operations with the database."""

from typing import List
from pathlib import Path

from tinydb import TinyDB

from chesstournament import DB_READ_ERROR, DB_WRITE_ERROR, SUCCESS, ERRORS
from chesstournament.models.player import Player

DEFAULT_DB_LOCATION = Path.home() / '.chess_tournament.json'



def create_database(db_path: Path = DEFAULT_DB_LOCATION) -> int:
    """Creates a local database file at 'db_path'."""
    try:
        TinyDB(db_path)
    except OSError:
        return DB_WRITE_ERROR

    return SUCCESS


class DatabaseException(Exception):
    """The database module raises this when an exception occurs."""
    def __init__(self, code):
        self.code = code
        self.message = ERRORS[code]


class PlayersManager:
    """Controller that manages players."""
    def __init__(self, db_path: str) -> None:
        try:
            self._database = TinyDB(db_path)
        except Exception:
            raise DatabaseException(DB_READ_ERROR)

    def add(self, new_player: Player) -> int:
        del new_player.id

        try:
            new_player.id = self._database.table('players').insert(new_player)
            return new_player.id
        except Exception:
            raise DatabaseException(DB_WRITE_ERROR)

    def get_all(self) -> List[Player]:
        try:
            players = self._database.table('players').all()
            return [Player(**player, id=player.doc_id) for player in players]
        except Exception:
            raise DatabaseException(DB_READ_ERROR)

    def get_by_id(self, player_id: int):
        try:
            player = self._database.table('players').get(doc_id=player_id)
            return Player(**player, id=player.doc_id)
        except:
            raise DatabaseException(DB_READ_ERROR)

    def update_one(self, player: Player):
        player_id = player.id
        del player.id

        try:
            doc_id, = self._database.table('players').update(player, doc_ids=[player_id])
            player.id = doc_id
            return doc_id
        except Exception:
            raise DatabaseException(DB_WRITE_ERROR)
