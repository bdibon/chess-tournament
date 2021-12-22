from typing import List

from tinydb import TinyDB

from chesstournament.models.tournament import Tournament


class TournamentsManager:
    """Controller that manages players."""

    def __init__(self, db_path: str) -> None:
        self._database = TinyDB(db_path)

    def add(self, new_tournament: Tournament) -> int:
        del new_tournament.id
        new_tournament.id = self._database.table('tournaments').insert(new_tournament)
        return new_tournament.id

    def get_all(self) -> List[Tournament]:
        tournaments = self._database.table('tournaments').all()
        return [Tournament(**tournament, id=tournament.doc_id) for tournament in tournaments]

    def get_by_id(self, tournament_id: int):
        tournament = self._database.table('tournaments').get(doc_id=tournament_id)
        return Tournament(**tournament, id=tournament.doc_id)

    def update_one(self, tournament: Tournament):
        tournament_id = tournament.id
        del tournament.id
        doc_id, = self._database.table('tournaments').update(tournament, doc_ids=[tournament_id])
        tournament.id = doc_id
        return doc_id
