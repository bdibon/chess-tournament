"""This module provides the Tournament class."""
from collections.abc import Mapping
from datetime import datetime
from typing import Union, List, Optional

from chesstournament.models.player import TournamentPlayer

TIME_CONTROLS = ['bullet', 'blitz', 'rapid']
TIME_FORMAT_ROUND = '%Y-%m-%d - %H:%M'
TIME_FORMAT_TOURNAMENT = '%Y-%m-%d'


class TournamentException(Exception):
    """The tournament module raises this when it is misused."""

    def __init__(self, message: str, field: str = '') -> None:
        """
        Args
            message (str): description of the error
            field (str): name of the attribute involved
        """
        self.message = message
        self.field = field
        super().__init__(self.message)


class Round:
    def __init__(self, name: str, matches: list, start_date: Union[str, None] = None,
                 end_date: Union[str, None] = None) -> None:
        self._name = name
        self._matches = matches
        self._start_date = start_date
        self._end_date = end_date

    def __str__(self):
        return str({
            'name': self._name,
            'matches': self._matches,
            'start_date': self._start_date,
            'end_date': self._end_date
        })

    def __repr__(self):
        return f"Round({self._name}, {self._matches}, {self._start_date}, {self._end_date})"

    @property
    def name(self):
        return self._name

    @property
    def matches(self):
        return self._matches

    @matches.setter
    def matches(self, saved_matches):
        if saved_matches is None:
            self._matches = []
        else:
            self._matches = saved_matches

    def new_match(self, player_1, player_2):
        match = ([player_1, None], [player_2, None])
        self._matches.append(match)
        return match

    @property
    def start_date(self):
        return self._start_date

    # todo: the controller should set the start_date when the round begins
    @start_date.setter
    def start_date(self, value):
        if value is not None:
            try:
                datetime.strptime(value, TIME_FORMAT_ROUND)
                self._start_date = value
            except ValueError:
                raise TournamentException(f'Invalid start_date for round (must be YYYY-mm-dd - HH:MM): {value}.')
        self._start_date = None

    @property
    def end_date(self):
        return self._end_date

    # todo: the controller should set the end_date when the round ends
    @end_date.setter
    def end_date(self, value):
        if value is not None:
            try:
                datetime.strptime(value, TIME_FORMAT_ROUND)
                self._end_date = value
            except ValueError:
                raise TournamentException(f'Invalid end_date for round (must be YYYY-mm-dd - HH:MM): {value}.')
        self._end_date = None


class Tournament(Mapping):
    def __init__(self,
                 name: str,
                 location: str,
                 number_of_rounds: int,
                 time_control: str,
                 description: str,
                 start_date: Union[str, None] = None,
                 end_date: Union[str, None] = None,
                 competitors: List[TournamentPlayer] = None,
                 rounds: List[Round] = None,
                 id: Optional[int] = None):
        self._name = name
        self._location = location
        self._number_of_rounds = number_of_rounds
        self._description = description

        self.time_control = time_control
        self.start_date = start_date
        self.end_date = end_date
        self.competitors = competitors
        self.rounds = rounds

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
        return f"Tournament({self._name}, {self._location}, {self._number_of_rounds}, {self._time_control}," \
               f" {self._description}, {self._competitors}, {self._rounds}, {self._start_date}, {self._end_date})"

    @property
    def name(self):
        return self._name

    @property
    def location(self):
        return self._location

    @property
    def number_of_rounds(self):
        return self._number_of_rounds

    @property
    def time_control(self):
        return self._time_control

    @time_control.setter
    def time_control(self, value):
        if value not in TIME_CONTROLS:
            raise ValueError(f"time_control must be one of {', '.join(TIME_CONTROLS)}.")
        self._time_control = value

    @property
    def description(self):
        return self._description

    @property
    def competitors(self):
        return self._competitors

    @competitors.setter
    def competitors(self, saved_competitors):
        if saved_competitors is None:
            self._competitors = []
        else:
            self._competitors = saved_competitors

    def add_competitor(self, new_competitor):
        if not isinstance(new_competitor, TournamentPlayer):
            raise ValueError("Competitors must be instances of TournamentPlayer.")
        self._competitors.append(new_competitor)

    @property
    def rounds(self):
        return self._rounds

    @rounds.setter
    def rounds(self, saved_rounds):
        if saved_rounds is None:
            self._rounds = []
        else:
            self._rounds = saved_rounds

    def add_round(self, new_round):
        if len(self._rounds) == self._number_of_rounds:
            raise AttributeError(f"This tournament is over ({self._number_of_rounds} max).")
        if not isinstance(new_round, Round):
            raise ValueError("Rounds must be instances of Round.")

        self._rounds.append(new_round)
        if len(self._rounds) == self._number_of_rounds:
            self._end_date = datetime.now().strftime(TIME_FORMAT_TOURNAMENT)

    @property
    def start_date(self):
        return self._start_date

    @start_date.setter
    def start_date(self, value):
        if value is not None:
            try:
                datetime.strptime(value, TIME_FORMAT_TOURNAMENT)
                self._start_date = value
            except ValueError:
                raise TournamentException(f'Invalid start_date for tournament (must be YYYY-mm-dd): {value}.')
        else:
            self._start_date = None

    @property
    def end_date(self):
        return self._end_date

    @end_date.setter
    def end_date(self, value):
        if value is not None:
            try:
                datetime.strptime(value, TIME_FORMAT_TOURNAMENT)
                self._end_date = value
            except ValueError:
                raise TournamentException(f'Invalid end_date for tournament (must be YYYY-mm-dd): {value}.')
        else:
            self._end_date = None
