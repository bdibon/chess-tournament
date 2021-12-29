"""This module provides the Tournament class."""

import math
from collections.abc import Mapping
from datetime import datetime
from typing import Union, List, Optional, Tuple

from chesstournament.models.player import TournamentPlayer

TIME_CONTROLS = ['bullet', 'blitz', 'rapid']
TIME_FORMAT_ROUND = '%Y-%m-%d - %H:%M'
TIME_FORMAT_TOURNAMENT = '%Y-%m-%d'
MIN_NUMBER_OF_PLAYERS = 2


class TournamentException(Exception):
    """The tournament module raises this when it is misused."""

    def __init__(self, message: str) -> None:
        """
        Args
            message (str): description of the error
        """
        self.message = message
        super().__init__(self.message)


class Round(Mapping):
    def __init__(self, name: str, matches: list, start_date: Union[str, None] = None,
                 end_date: Union[str, None] = None) -> None:
        self._name = name
        self._matches = matches
        self._start_date = start_date or datetime.now().strftime(TIME_FORMAT_ROUND)
        self._end_date = end_date

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
        return f"Round({self._name}, {self._matches}, {self._start_date}, {self._end_date})"

    def finish(self):
        self.end_date = datetime.now().strftime(TIME_FORMAT_ROUND)

    def serialize(self):
        dump = dict(self)
        lean_matches = []

        for match in dump['matches']:
            p1, score_p1 = match[0]
            p2, score_p2 = match[1]

            p1_id = getattr(p1, 'id', None)
            p2_id = getattr(p2, 'id', None)
            lean_matches.append(([p1_id, score_p1], [p2_id, score_p2]))

        dump['matches'] = lean_matches
        return dump

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

    @property
    def start_date(self):
        return self._start_date

    @start_date.setter
    def start_date(self, value):
        try:
            datetime.strptime(value, TIME_FORMAT_ROUND)
            self._start_date = value
        except ValueError:
            raise TournamentException(f'Invalid start_date for round (must be YYYY-mm-dd - HH:MM): {value}.')

    @property
    def end_date(self):
        return self._end_date

    @end_date.setter
    def end_date(self, value):
        try:
            datetime.strptime(value, TIME_FORMAT_ROUND)
            self._end_date = value
        except ValueError:
            raise TournamentException(f'Invalid end_date for round (must be YYYY-mm-dd - HH:MM): {value}.')

    @property
    def all_matches_completed(self):
        for m in self.matches:
            p1_data, p2_data = m
            p1, p1_score, = p1_data
            p2, p2_score, = p2_data

            if p1_score is None or p2_score is None:
                return False
        return True


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
        self._number_of_rounds = int(number_of_rounds)
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

    def add_competitor(self, new_competitor: TournamentPlayer):
        """Add a new competitor to the tournament."""
        if self.has_competitors and not isinstance(self._competitors[0], TournamentPlayer):
            raise TournamentException(
                "Competitors are not instances of TournamentPlayer, you might need to enrich the data."
            )
        if not isinstance(new_competitor, TournamentPlayer):
            raise TournamentException("Competitors must be instances of TournamentPlayer.")
        self._competitors.append(new_competitor)

    def add_round(self, name: str, fixtures: List[Tuple[TournamentPlayer]]):
        """Add a new round to the tournament."""
        if self.is_over:
            raise TournamentException(f"This tournament is over ({self._number_of_rounds} max).")

        matches = []
        for (p, q) in fixtures:
            p_score = None
            q_score = None

            if p is None:
                q.wins()
                p_score = 0
                q_score = 1
            if q is None:
                p.wins()
                p_score = 1
                q_score = 0

            p_data = [p, p_score]
            q_data = [q, q_score]
            matches.append((p_data, q_data))

        new_round = Round(name, matches)
        self._rounds.append(new_round)

    def serialize(self):
        """Returns a lean dictionary of the instance."""
        dump = dict(self)
        dump['competitors'] = [comp.serialize() for comp in dump['competitors']]
        dump['rounds'] = [ro.serialize() for ro in dump['rounds']]
        return dump

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
            raise TournamentException(f"time_control must be one of {', '.join(TIME_CONTROLS)}.")
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

    @property
    def rounds(self):
        return self._rounds

    @rounds.setter
    def rounds(self, saved_rounds):
        if saved_rounds is None:
            self._rounds = []
        else:
            self._rounds = saved_rounds

    @property
    def number_of_competitors(self):
        return len(self._competitors)

    @property
    def first_round(self):
        return self._rounds[1] if len(self._rounds) >= 1 else None

    @property
    def last_round(self):
        return self._rounds[-1] if len(self._rounds) >= 1 else None

    @property
    def matches_per_round(self):
        return math.ceil(self.number_of_competitors / 2)

    @property
    def has_started(self):
        return len(self._rounds)

    @property
    def has_competitors(self):
        return len(self._competitors)

    @property
    def has_enough_competitors(self):
        return len(self._competitors) >= MIN_NUMBER_OF_PLAYERS

    @property
    def is_over(self):
        return len(self._rounds) >= self._number_of_rounds

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
