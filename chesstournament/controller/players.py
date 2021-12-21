"""This module defines the controller to manage players."""
from enum import Flag, auto
from typing import List

from tinydb import TinyDB

from ..model.player import Player


class PlayerSort(Flag):
    """Sorting flags for players"""
    NONE = 0
    ALPHA = auto()
    ELO = auto()


class PlayersManager:
    """Controller that manages players."""
    def __init__(self, db_path: str) -> None:
        self._database = TinyDB(db_path)

    def add(self, new_player: Player) -> int:
        del new_player.id
        new_player.id = self._database.table('players').insert(new_player)
        return new_player.id

    def get_all(self) -> List[Player]:
        players = self._database.table('players').all()
        return [Player(**player, id=player.doc_id) for player in players]

    def get_by_id(self, player_id: int):
        player = self._database.table('players').get(doc_id=player_id)
        return Player(**player, id=player.doc_id)

    def update_one(self, player: Player):
        player_id = player.id
        del player.id
        doc_id, = self._database.table('players').update(player, doc_ids=[player_id])
        player.id = doc_id
        return doc_id


def sort_players(players: List[Player], flag: PlayerSort = PlayerSort.NONE) -> None:
    """Sort players according to the specified flag. Many flags results in undefined behavior."""

    def _sort_alpha(player):
        return player.last_name

    def _sort_elo(player):
        return player.elo

    if flag == PlayerSort.NONE:
        return None
    if flag == PlayerSort.ALPHA:
        players.sort(key=_sort_alpha)
    if flag == PlayerSort.ELO:
        players.sort(key=_sort_elo, reverse=True)
