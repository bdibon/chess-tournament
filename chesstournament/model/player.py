"""This module provides the Player class."""

from collections.abc import Mapping

from datetime import datetime
from typing import Optional

SEXES = {'m': 'male', 'f': 'female'}


class PlayerException(Exception):
    """The player module raises this when the module is misused."""

    def __init__(self, message: str, field: str = '') -> None:
        """
        Args
            message (str): description of the error
            field (str): name of the attribute involved
        """
        self.message = message
        self.field = field
        super().__init__(self.message)


class Player(Mapping):
    def __init__(self,
                 first_name: str,
                 last_name: str,
                 birth_date: str,
                 sex: str,
                 elo: int,
                 id: Optional[int] = None) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.sex = sex
        self.elo = elo

        self.id = id

    def __len__(self):
        return len(self.__dict__)

    def __getitem__(self, item):
        return getattr(self, item)

    def __iter__(self):
        return iter(key.lstrip('_') for key in self.__dict__)

    def __str__(self):
        dict_representation = {key.lstrip('_'): value for key, value in self.__dict__.items()}
        return str(dict_representation)

    def __repr__(self):
        return f"{self.__class__.__name__}" \
               f"({self._first_name}, {self._last_name}, {self._birth_date}, {self._sex}, {self._elo})"

    @property
    def first_name(self):
        return self._first_name

    @first_name.setter
    def first_name(self, value):
        self._first_name = value.capitalize()

    @property
    def last_name(self):
        return self._last_name

    @last_name.setter
    def last_name(self, value):
        self._last_name = value.upper()

    @property
    def birth_date(self):
        return self._birth_date

    @birth_date.setter
    def birth_date(self, value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
            self._birth_date = value
        except ValueError:
            raise PlayerException("Player's date of birth must be in the YYYY-MM-DD format.")

    @property
    def sex(self) -> str:
        return self._sex

    @sex.setter
    def sex(self, value):
        value = value.lower()

        if len(value) == 1 and value in SEXES:
            self._sex = SEXES[value]
        elif value in SEXES.values():
            self._sex = value
        else:
            raise PlayerException(f"Invalid sex value ({value}) for Player.")

    @property
    def elo(self) -> int:
        return self._elo

    @elo.setter
    def elo(self, value: int):
        if value < 100:
            raise PlayerException("Elo rating cannot be below 100.")
        self._elo = value


class TournamentPlayer(Player):
    def __init__(self,
                 first_name: str,
                 last_name: str,
                 birth_date: str,
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
