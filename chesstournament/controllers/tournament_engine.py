"""This module contains the logic to run a tournament."""

import itertools
from operator import attrgetter

from chesstournament import view
from chesstournament.models.player import TournamentPlayer
from chesstournament.models.tournament import Round

# Data headers.
COMPETITOR_HEADER = (
    "id", "first_name", "last_name", "elo", 'score'
)

MATCH_HISTORY_HEADER = ("round_name", "player_1", "player_2", "outcome")

# Menu constants.
(
    COMPETITOR_MENU_ID,
    COMPETITOR_MENU_NAME,
    COMPETITOR_MENU_LIST_PLAYERS,
    COMPETITOR_MENU_LAUNCH
) = range(1, 5)

(
    MAIN_MENU_HEADER,
    MAIN_MENU_SCOREBOARD,
    MAIN_MENU_LIST_ROUNDS,
    MAIN_MENU_MATCH_HISTORY,
    MAIN_MENU_CURRENT_ROUND
) = range(1, 6)

ROUND_MENU_BACK = 1

(
    MATCH_MENU_BACK,
    MATCH_MENU_P1_WINS,
    MATCH_MENU_P2_WINS,
    MATCH_MENU_DRAW
) = range(1, 5)

class TournamentEngineException(Exception):
    """The TournamentEngine class raises this when it is misused."""

    def __init__(self, message: str) -> None:
        """
        Args
            message (str): description of the error
        """
        self.message = message
        super().__init__(self.message)


class TournamentEngine:
    """This gathers the required functionality by the run tournament command."""

    ROUND_MENU_FINISH = 99

    def __init__(self, tournament, players_registry, tournament_registry):
        self.tournament = tournament
        self.players_registry = players_registry
        self.tournament_registry = tournament_registry

    # Public methods.
    def prepare(self):
        """Triggers an interaction with the user to add participants."""
        if self.tournament.has_competitors:
            self._populate_competitors()

        self._display_tournament_header()
        while True:
            self._add_new_competitor()

    def resume(self) -> None:
        """Resume tournament execution."""
        if not self._has_populated_competitors():
            self._populate_competitors()
        if not self._has_populated_rounds():
            self._populate_rounds()

        # Main menu.
        self._display_tournament_header()
        while True:
            main_menu_item = self._prompt_main_menu()

            current_round = self.tournament.last_round
            if main_menu_item == MAIN_MENU_HEADER:
                self._display_tournament_header()
            if main_menu_item == MAIN_MENU_SCOREBOARD:
                self._display_scoreboard()
            elif main_menu_item == MAIN_MENU_LIST_ROUNDS:
                self._display_rounds_list()
            elif main_menu_item == MAIN_MENU_MATCH_HISTORY:
                self._display_match_history()
            elif main_menu_item == MAIN_MENU_CURRENT_ROUND:
                while True:
                    # Current round menu.
                    self._display_round_infos(current_round)
                    round_menu_item = self._prompt_round_menu(current_round)

                    if round_menu_item == ROUND_MENU_BACK:
                        break
                    elif round_menu_item == self.ROUND_MENU_FINISH:
                        current_round.finish()
                        self._save_tournament()
                        self._launch_next_round()
                        break
                    else:
                        # Match menu.
                        current_match = current_round.matches[round_menu_item - (ROUND_MENU_BACK + 1)]
                        while True:
                            self._display_match_infos(current_match)
                            match_menu_item = self._prompt_match_menu(current_match)

                            if match_menu_item == MATCH_MENU_BACK:
                                break
                            elif match_menu_item == MATCH_MENU_P1_WINS:
                                self._update_match_outcome(current_match, MATCH_MENU_P1_WINS)
                            elif match_menu_item == MATCH_MENU_P2_WINS:
                                self._update_match_outcome(current_match, MATCH_MENU_P2_WINS)
                            elif match_menu_item == MATCH_MENU_DRAW:
                                self._update_match_outcome(current_match, MATCH_MENU_DRAW)

    # Private methods
    def _has_populated_competitors(self) -> bool:
        """Checks whether it should populate competitors or not."""
        return self.tournament.has_competitors and isinstance(self.tournament.competitors[0], TournamentPlayer)

    def _populate_competitors(self) -> None:
        """Populate competitors with data from the players table."""
        t_players = []
        for lean_player in self.tournament.competitors:
            fat_player = self.players_registry.find(lean_player['id'])
            t_players.append(TournamentPlayer(**fat_player, score=lean_player['score'],
                                              previous_opponents=lean_player['previous_opponents']))
        self.tournament.competitors = t_players

    def _add_new_competitor(self) -> None:
        """Prompts the user to add a competitor, add it to the current tournament and save it."""
        menu_item = self._prompt_new_competitor_menu()
        player_id = first_name = last_name = None

        if menu_item == COMPETITOR_MENU_ID:
            player_id = view.prompt_value("Player's id", int)
            competitor_ids = [comp.id for comp in self.tournament.competitors]
            if player_id in competitor_ids:
                raise TournamentEngineException(f"Player with id={player_id} is already in the list of competitors.")
        elif menu_item == COMPETITOR_MENU_NAME:
            first_name = view.prompt_value("First name", str)
            last_name = view.prompt_value("Last name", str)
        elif menu_item == COMPETITOR_MENU_LIST_PLAYERS:
            self._display_scoreboard()
            return
        elif menu_item == COMPETITOR_MENU_LAUNCH:
            self._launch()
            return
        else:
            raise TournamentEngineException(f"Invalid option {menu_item}")

        new_player = self.players_registry.find(player_id, first_name, last_name)
        if new_player is None:
            raise TournamentEngineException("Player not found.")

        t_player = TournamentPlayer.from_player(new_player)
        self.tournament.add_competitor(t_player)
        self._save_tournament()

    def _prompt_new_competitor_menu(self) -> int:
        """Get input for new competitor."""
        menu_items = {
            COMPETITOR_MENU_ID: "Add player by id",
            COMPETITOR_MENU_NAME: "Add player by name",
            COMPETITOR_MENU_LIST_PLAYERS: "List registered players"
        }

        if self.tournament.has_enough_competitors:
            menu_items[COMPETITOR_MENU_LAUNCH] = "Launch tournament (irreversible)"

        choice = view.prompt_menu(menu_items)
        return choice

    def _has_populated_rounds(self) -> bool:
        """Checks whether it should populate rounds or not."""
        if not self.tournament.has_started:
            return True

        first_round = self.tournament.rounds[0]
        sample_match = first_round['matches'][0]
        sample_player = sample_match[0][0]

        return isinstance(sample_player, TournamentPlayer)

    def _populate_rounds(self) -> None:
        """Populate rounds with data from the tournament's competitors."""
        if not self._has_populated_competitors():
            self._populate_competitors()

        rounds = []
        for lean_round in self.tournament.rounds:
            matches = lean_round['matches']
            for match in matches:
                p1_id = match[0][0]
                p2_id = match[1][0]

                if p1_id is not None:
                    tp1, = (tp for tp in self.tournament.competitors if tp.id == p1_id)
                else:
                    tp1 = None
                if p2_id is not None:
                    tp2, = (tp for tp in self.tournament.competitors if tp.id == p2_id)
                else:
                    tp2 = None

                match[0][0] = tp1
                match[1][0] = tp2

            rounds.append(Round(lean_round['name'], matches, lean_round['start_date'], lean_round['end_date']))

        self.tournament.rounds = rounds

    def _save_tournament(self):
        """Persist current tournament's state."""
        self.tournament_registry.update_one(self.tournament)

    def _update_match_outcome(self, match, outcome):
        """Update a match's outcome."""
        player1_data, player2_data = match
        player1, score_p1 = player1_data
        player2, score_p2 = player2_data

        # Prevent duplicates when user updates match.
        if player1.last_opponent != player2.id:
            player1.add_opponent(player2)
        if player2.last_opponent != player1.id:
            player2.add_opponent(player1)

        # Reset player's "tournament" score.
        player1.score = player1.score - (score_p1 or 0)
        player2.score = player2.score - (score_p2 or 0)
        if outcome == MATCH_MENU_P1_WINS:
            player1.wins()
            player1_data[1] = 1
            player2_data[1] = 0
        elif outcome == MATCH_MENU_P2_WINS:
            player2.wins()
            player1_data[1] = 0
            player2_data[1] = 1
        elif outcome == MATCH_MENU_DRAW:
            player1.draws()
            player2.draws()
            player1_data[1] = 0.5
            player2_data[1] = 0.5
        else:
            raise TournamentEngineException("Invalid match outcome.")

        self._save_tournament()

    def _sort_competitors(self) -> list:
        """Sort competitors by their score and elo."""
        return sorted(self.tournament.competitors, key=attrgetter('score', 'elo'), reverse=True)

    def _display_scoreboard(self):
        """Display competitors of the current tournament."""
        sorted_competitors = self._sort_competitors()
        view.print_tabular_data(COMPETITOR_HEADER, sorted_competitors, f"{self.tournament.name} - Scoreboard")

    def _display_tournament_header(self):
        """Display basic info about the current tournament."""
        view.print_tournament_header(self.tournament)

        if self.tournament.is_over:
            view.print_raw("\nThis tournament is over.\n")

    def _display_round_infos(self, current_round: Round):
        round_idx = self.tournament.rounds.index(current_round)

        matches = []
        for idx, m in enumerate(current_round.matches, start=1):
            player1_data, player2_data = m

            player1, score_p1 = player1_data
            player2, score_p2 = player2_data

            player1_fullname = getattr(player1, 'full_name', 'N/A')
            player2_fullname = getattr(player2, 'full_name', 'N/A')

            if score_p1 == 1:
                outcome = f"{player1_fullname} WINS"
            elif score_p2 == 1:
                outcome = f"{player2_fullname} WINS"
            elif score_p1 == 0.5:
                outcome = "DRAW"
            else:
                outcome = "N/A"

            m_data = {
                'match #': f"match {idx}",
                'player 1': player1_fullname,
                'player 2': player2_fullname,
                'outcome': outcome
            }
            matches.append(m_data)

        heading = f"{current_round.name} ({round_idx + 1}/{self.tournament.number_of_rounds})"
        description = f"\nStarted at: {current_round.start_date}" \
                      f"\nEnded at: {getattr(current_round, 'end_date', 'N/A')}\n"

        view.print_tabular_data(header=('match #', 'player 1', 'player 2', 'outcome'), items=matches,
                                heading=heading, description=description)

    def _display_state(self):
        """Display the tournament current state."""
        # display tournament infos
        self._display_tournament_header()

        # display competitors
        self._display_scoreboard()

        # display the current round state
        self._display_round_infos(self.tournament.last_round)

    def _prompt_main_menu(self) -> int:
        menu_items = {
            MAIN_MENU_HEADER: "Header",
            MAIN_MENU_SCOREBOARD: "Scoreboard",
            MAIN_MENU_LIST_ROUNDS: "List rounds",
            MAIN_MENU_MATCH_HISTORY: "Match history"
        }

        if not self.tournament.is_over:
            menu_items[MAIN_MENU_CURRENT_ROUND] = "Current round"

        choice = view.prompt_menu(menu_items)
        return choice

    def _prompt_round_menu(self, current_round: Round) -> int:
        menu_items = dict()
        menu_items[ROUND_MENU_BACK] = "Back"

        for idx, m in enumerate(current_round.matches):
            p1_data, p2_data = m
            p1, p1_score = p1_data
            p2, p2_score = p2_data

            if p1 and p2:
                menu_items[idx + ROUND_MENU_BACK + 1] = f"{p1.full_name} vs {p2.full_name}"

        if current_round.all_matches_completed:
            self.ROUND_MENU_FINISH = len(menu_items) + 1
            menu_items[self.ROUND_MENU_FINISH] = "Mark as finished (irreversible)"

        choice = view.prompt_menu(menu_items)
        return choice

    @staticmethod
    def _display_match_infos(match):
        p1_data, p2_data = match
        p1, p1_score = p1_data
        p2, p2_score = p2_data

        view.print_match(p1.full_name, p2.full_name, p1_score, p2_score)

    @staticmethod
    def _prompt_match_menu(match) -> int:
        menu_items = dict()
        menu_items[MATCH_MENU_BACK] = "Back"

        p1_data, p2_data = match
        p1, p1_score = p1_data
        p2, p2_score = p2_data

        menu_items[MATCH_MENU_P1_WINS] = f"{p1.full_name} wins"
        menu_items[MATCH_MENU_P2_WINS] = f"{p2.full_name} wins"
        menu_items[MATCH_MENU_DRAW] = "Draw"

        choice = view.prompt_menu(menu_items)
        return choice

    def _display_rounds_list(self):
        matches_per_round = self.tournament.matches_per_round
        view.print_rounds(self.tournament.name, self.tournament.rounds, matches_per_round)

    def _display_match_history(self):
        match_history = []
        for r in self.tournament.rounds:
            for m in r.matches:
                player1_data, player2_data = m

                player1, score_p1 = player1_data
                player2, score_p2 = player2_data

                player1_fullname = getattr(player1, 'full_name', 'N/A')
                player2_fullname = getattr(player2, 'full_name', 'N/A')
                player1_info = f"{player1_fullname} (+{score_p1} pts)"
                player2_info = f"{player2_fullname} (+{score_p2} pts)"

                if score_p1 == 1:
                    outcome = f"{player1.last_name} WINS"
                elif score_p2 == 1:
                    outcome = f"{player2.last_name} WINS"
                elif score_p1 == 0.5:
                    outcome = "DRAW"
                else:
                    player1_info = f"{player1_fullname}"
                    player2_info = f"{player2_fullname}"
                    outcome = "N/A"
                match_history.append(dict(round_name=r.name, player_1=player1_info,
                                          player_2=player2_info, outcome=outcome))

        view.print_tabular_data(MATCH_HISTORY_HEADER, match_history,
                                heading=f"{self.tournament.name} - Match History")

    def _prompt_new_round(self):
        round_name = view.prompt_new_round(self.tournament.name, len(self.tournament.rounds) + 1)
        return round_name

    def _launch(self) -> None:
        """Creates the first round of the tournament."""
        # Sort players by elo.
        self.tournament.competitors = self._sort_competitors()

        # Split the resulting list in half.
        middle_idx = len(self.tournament.competitors) // 2
        top_players = self.tournament.competitors[:middle_idx]
        bot_players = self.tournament.competitors[middle_idx:]

        # Make pairs with players of each list.
        fixtures = list(itertools.zip_longest(top_players, bot_players))

        # Add first round to the tournament.
        round_name = self._prompt_new_round()
        self.tournament.add_round(round_name, fixtures)

        self._save_tournament()
        self.resume()

    def _launch_next_round(self) -> None:
        if self.tournament.is_over:
            return

        # Sort players by score, then by elo.
        self.tournament.competitors = self._sort_competitors()

        busy_players = []
        fixtures = []
        for ida, player_a in enumerate(self.tournament.competitors[:-1], start=0):
            if player_a in busy_players:
                continue
            for idb, player_b in enumerate(self.tournament.competitors[ida + 1:], start=ida + 1):
                if player_b in busy_players:
                    continue

                if not player_a.has_faced(player_b):
                    fixtures.append((player_a, player_b))
                    busy_players.append(player_b)
                    break

                # player_a has faced every other players, make him play with the next player on the scoreboard.
                if idb == len(self.tournament.competitors) - 1:
                    next_player = self.tournament.competitors[ida + 1]
                    fixtures.append((player_a, next_player))
                    busy_players.append(next_player)

        # Check expected number of fixtures, regarding the number of competitors (odd number of competitors).
        if len(fixtures) < self.tournament.matches_per_round:
            busy_ids = {p.id for p in busy_players}
            all_ids = {p.id for p in self.tournament.competitors}
            single_player_id = (all_ids - busy_ids).pop()
            single_player = next((p for p in self.tournament.competitors if p.id == single_player_id))
            fixtures.append((single_player, None))

        round_name = self._prompt_new_round()
        self.tournament.add_round(round_name, fixtures)
        self._save_tournament()
