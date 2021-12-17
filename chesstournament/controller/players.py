"""This module defines the controller to manage players."""

from tinydb import TinyDB

from ..model.player import Player


class PlayersManager:
    def __init__(self, db_path: str) -> None:
        self._database = TinyDB(db_path)

    def save(self, new_player: Player) -> int:
        new_player.id = self._database.table('players').insert(new_player)
        return new_player.id
