from chesstournament.views.players import PlayerCLIView
from chesstournament.views.tournaments import TournamentCLIView
from chesstournament.views.utils import UtilityCLIView

ROUND_NAME_PROMPT = 'round name'


class CLIView:
    def __init__(self):
        self.utils_view = UtilityCLIView()
        self.player_view = PlayerCLIView()
        self.tournament_view = TournamentCLIView()

    # General purpose methods.
    def print_success(self, message: str) -> None:
        self.utils_view.print_success(message)

    def print_error(self, message: str) -> None:
        self.utils_view.print_error(message)

    def print_raw(self, message: str) -> None:
        self.utils_view.print_raw(message)

    def print_tabular_data(self, header: tuple, items: list, heading: str = None) -> None:
        self.utils_view.print_tabular_data(header, items, heading)

    def prompt_value(self, description: str, expected_type: type = None, default_value: str = None) -> any:
        return self.utils_view.prompt_value(description, expected_type, default_value)

    def prompt_menu(self, menu_items: dict) -> any:
        return self.utils_view.prompt_menu(menu_items)

    # Player methods.
    def prompt_for_new_player(self) -> dict:
        return self.player_view.prompt_for_new_player()

    def print_players(self, players: list) -> None:
        self.player_view.print_players(players)

    # Tournament methods.
    def prompt_for_new_tournament(self) -> dict:
        return self.tournament_view.prompt_for_new_tournament()

    def print_tournaments(self, tournaments: list) -> None:
        self.tournament_view.print_tournaments(tournaments)

    # Running tournament methods.
    def print_tournament_header(self, tournament) -> None:
        self.print_raw(f"[ {tournament.name} - Overview ]")
        self.print_tournaments([tournament])

    def print_match(self, p1_name: str, p2_name: str, p1_score: int, p2_score: int) -> None:
        self.tournament_view.print_match(p1_name, p2_name, p1_score, p2_score)

    def print_rounds(self, tournament_name: str, rounds: list, matches_per_round: int) -> None:
        self.tournament_view.print_rounds(tournament_name, rounds, matches_per_round)

    def prompt_new_round(self, tournament_name: str, round_number: int) -> str:
        self.print_raw(f"[ {tournament_name} - New round ]")
        round_name = self.prompt_value(ROUND_NAME_PROMPT, str, f"Round {round_number}")
        return round_name
