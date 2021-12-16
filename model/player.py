"""This module provides the Player class."""

from datetime import date
from typing import Union

SEXES = ['male', 'female']


class Player:
    def __init__(self,
                 first_name: str,
                 last_name: str,
                 birth_date: Union[date, str],
                 sex: str,
                 elo: int) -> None:
        self._first_name = first_name
        self._last_name = last_name
        self._sex = sex
        self.elo = elo

        if isinstance(birth_date, date):
            self._birth_date = birth_date
        else:
            self._birth_date = date.fromisoformat(birth_date)

    def __str__(self):
        return str({
            'first_name': self._first_name,
            'last_name': self._last_name,
            'birth_date': str(self._birth_date),
            'sex': self._sex,
            'elo': self._elo,
        })

    def __repr__(self):
        return f"{self.__class__.__name__}" \
               f"({self._first_name}, {self._last_name}, {str(self._birth_date)}, {self._sex}, {self._elo})"

    @property
    def first_name(self):
        return self._first_name

    @property
    def last_name(self):
        return self._last_name

    @property
    def birth_date(self):
        return self._birth_date

    @property
    def sex(self) -> str:
        return self._sex

    @property
    def elo(self) -> int:
        return self._elo

    @elo.setter
    def elo(self, value: int):
        if value < 100:
            raise ValueError("Elo rating cannot be below 100.")
        self._elo = value


class TournamentPlayer(Player):
    def __init__(self,
                 first_name: str,
                 last_name: str,
                 birth_date: date,
                 sex: str,
                 elo: int,
                 previous_opponents: list,
                 score: float = 0) -> None:
        super().__init__(first_name,
                         last_name,
                         birth_date,
                         sex,
                         elo)
        self._score = score
        self._previous_opponents = previous_opponents

    def __str__(self):
        return str({
            'first_name': self._first_name,
            'last_name': self._last_name,
            'birth_date': str(self._birth_date),
            'sex': self._sex,
            'elo': self._elo,
            'score': self._score,
            'previous_opponents': self._previous_opponents

        })

    def __repr__(self):
        return f"{self.__class__.__name__}" \
               f"({self._first_name}, {self._last_name}, {str(self._birth_date)}, {self._sex}, {self._elo}," \
               f" {self._score}, {self._previous_opponents})"

    @property
    def score(self):
        return self._score

    def wins(self):
        self._score += 1

    def draws(self):
        self._score += 0.5

    @property
    def previous_opponents(self):
        return self._previous_opponents

    @previous_opponents.setter
    def previous_opponents(self, saved_opponents):
        if saved_opponents is None:
            self._previous_opponents = []
        else:
            self._previous_opponents = saved_opponents

    def add_opponent(self, new_opponent):
        if not isinstance(new_opponent, TournamentPlayer):
            raise ValueError('A TournamentPlayer opponents must be another TournamentPlayer.')
        self._previous_opponents.append(new_opponent)

# me = Player('Boris', 'DIBON', '1992-08-12', 'male', 1200)
# print(me)
