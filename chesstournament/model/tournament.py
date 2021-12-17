"""This module provides the Tournament class."""
from datetime import date
from typing import Union, List

from player import TournamentPlayer

TIME_CONTROLS = ['bullet', 'blitz', 'rapid']


class Round:
    def __init__(self, name: str, matches: list, start_date: Union[date, str, None] = None,
                 end_date: Union[date, str, None] = None) -> None:
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

    @start_date.setter
    def start_date(self, value):
        if value is None:
            self._start_date = date.today()
        elif type(value) is str:
            self._start_date = date.fromisoformat(value)
        else:
            self._start_date = date.today()

    @property
    def end_date(self):
        return self._end_date

    @end_date.setter
    def end_date(self, value):
        if type(value) is str:
            self._end_date = date.fromisoformat(value)
        else:
            self._end_date = value


class Tournament:
    def __init__(self,
                 name: str,
                 location: str,
                 number_of_rounds: int,
                 time_control: str,
                 description: str,
                 competitors: List[TournamentPlayer],
                 rounds: List[Round],
                 start_date: Union[date, str, None] = None,
                 end_date: Union[date, str, None] = None) -> None:
        self._name = name
        self._location = location
        self._number_of_rounds = number_of_rounds
        self._time_control = time_control
        self._description = description
        self._competitors = competitors
        self._rounds = rounds
        self._start_date = start_date
        self._end_date = end_date

    def __str__(self):
        return str({
            'name': self._name,
            'location': self._location,
            'number_of_rounds': self._number_of_rounds,
            'time_control': self._time_control,
            'description': self._description,
            'competitors': self._competitors,
            'rounds': self._rounds,
            'start_date': str(self._start_date),
            'end_date': str(self._end_date)
        })

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
            self._end_date = date.today()

    @property
    def start_date(self):
        return self._start_date

    @start_date.setter
    def start_date(self, value):
        if value is None:
            self._start_date = date.today()
        elif type(value) is str:
            self._start_date = date.fromisoformat(value)
        else:
            self._start_date = date.today()

    @property
    def end_date(self):
        return self._end_date
