"""This is the main controller of chesstournament."""

import itertools
from pathlib import Path
from typing import Optional

import typer

from chesstournament import __app_name__, __version__, config, ERRORS
from chesstournament import cli
from chesstournament.controllers import players, tournaments
from chesstournament.controllers.players import PlayerSort, sort_players
from chesstournament.models.database import DEFAULT_DB_LOCATION, DatabaseException, create_database
from chesstournament.models.player import PlayerException, TournamentPlayer
from chesstournament.models.tournament import TournamentException, Round

app = typer.Typer(add_completion=False)
app.add_typer(players.app, name='players', help='Manage players in the app.')
app.add_typer(tournaments.app, name='tournaments', help='Manage tournaments in the app')


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

    MAIN_MENU_SCOREBOARD = 1
    MAIN_MENU_LIST_ROUNDS = 2
    MAIN_MENU_CURRENT_ROUND= 3

    ROUND_MENU_BACK = 1
    ROUND_MENU_FINISH = 2

    MATCH_MENU_BACK = 1
    MATCH_MENU_P1_WINS = 2
    MATCH_MENU_P2_WINS = 3
    MATCH_MENU_DRAW = 4

    def __init__(self, tournament, players_registry, tournament_registry):
        self.tournament = tournament
        self.players_registry = players_registry
        self.tournament_registry = tournament_registry

    def has_populated_competitors(self) -> bool:
        """Checks whether it should populate competitors or not."""
        return self.tournament.has_competitors() and isinstance(self.tournament.competitors[0], TournamentPlayer)

    def populate_competitors(self) -> None:
        """Populate competitors with data from the players table."""
        t_players = []
        for lean_player in self.tournament.competitors:
            fat_player = self.players_registry.find(lean_player['id'])
            t_players.append(TournamentPlayer(**fat_player, score=lean_player['score'],
                                              previous_opponents=lean_player['previous_opponents']))
        self.tournament.competitors = t_players

    def add_new_competitor(self) -> None:
        """Prompts the user to add a competitor, add it to the current tournament and save it."""
        player_id, first_name, last_name = cli.tournaments.prompt_new_player()
        new_player = self.players_registry.find(player_id, first_name, last_name)
        if new_player is None:
            cli.utils.print_error("Player not found.")

        t_player = TournamentPlayer.from_player(new_player)
        self.tournament.add_competitor(t_player)
        self.save_tournament()

    def has_populated_rounds(self) -> bool:
        """Checks whether it should populate rounds or not."""
        if not self.tournament.has_started():
            return True

        first_round = self.tournament.rounds[0]
        sample_match = first_round['matches'][0]
        sample_player = sample_match[0][0]

        return isinstance(sample_player, TournamentPlayer)

    def populate_rounds(self) -> None:
        """Populate rounds with data from the tournament's competitors."""
        if not self.has_populated_competitors():
            self.populate_competitors()

        rounds = []
        for lean_round in self.tournament.rounds:
            matches = lean_round['matches']
            for match in matches:
                p1_id = match[0][0]
                p2_id = match[1][0]

                tp1, = (tp for tp in self.tournament.competitors if tp.id == p1_id)
                tp2, = (tp for tp in self.tournament.competitors if tp.id == p2_id)

                match[0][0] = tp1
                match[1][0] = tp2

            rounds.append(Round(lean_round['name'], matches, lean_round['start_date'], lean_round['end_date']))

        self.tournament.rounds = rounds

    def save_tournament(self):
        self.tournament_registry.update_one(self.tournament)

    def update_match_outcome(self, match, outcome):
        """Update a match's outcome."""
        player1_data, player2_data = match
        player1, score_p1 = player1_data
        player2, score_p2 = player2_data

        player1.add_opponent(player2)
        player2.add_opponent(player1)

        if outcome == self.MATCH_MENU_P1_WINS:
            # Reset player's "tournament" score.
            player1.score = player1.score - player1_data[1]
            player2.score = player2.score - player2_data[1]

            player1.wins()
            player1_data[1] = 1
            player2_data[1] = 0
        elif outcome == self.MATCH_MENU_P2_WINS:
            # Reset player's "tournament" score.
            player1.score = player1.score - player1_data[1]
            player2.score = player2.score - player2_data[1]

            player2.wins()
            player1_data[1] = 0
            player2_data[1] = 1
        elif outcome == self.MATCH_MENU_DRAW:
            # Reset player's "tournament" score.
            player1.score = player1.score - player1_data[1]
            player2.score = player2.score - player2_data[1]

            player1.draws()
            player2.draws()
            player1_data[1] = 0.5
            player2_data[1] = 0.5
        else:
            raise TournamentEngineException("Invalid match outcome.")

        self.save_tournament()

    def sort_competitors(self) -> list:
        return sorted(self.tournament.competitors, key=lambda player: player.score, reverse=True)

    def display_scoreboard(self):
        """Display competitors of the current tournament."""
        sorted_competitors = self.sort_competitors()
        cli.tournaments.print_scoreboard(self.tournament.name, sorted_competitors)

    def display_tournament_header(self):
        """Display basic info about the current tournament."""
        cli.tournaments.print_tournament_header(self.tournament)

    def display_round_infos(self, current_round: Round):
        round_idx = self.tournament.rounds.index(current_round)

        cli.tournaments.print_round_details(
            current_round.name,
            round_idx + 1,
            self.tournament.number_of_rounds,
            current_round.start_date,
            current_round.end_date,
            current_round.matches
        )

    def display_state(self):
        """Display the tournament current state."""
        # display tournament infos
        self.display_tournament_header()
        # display competitors
        self.display_scoreboard()

        # display the current round state
        self.display_round_infos(self.tournament.last_round)

    def prompt_main_menu(self) -> int:
        choice = cli.utils.print_menu({
            self.MAIN_MENU_SCOREBOARD: "Scoreboard",
            self.MAIN_MENU_LIST_ROUNDS: "List rounds",
            self.MAIN_MENU_CURRENT_ROUND: "Current round"
        })
        return choice

    def prompt_round_menu(self, current_round: Round) -> int:
        menu_items = dict()
        menu_items[self.ROUND_MENU_BACK] = "Back"

        gap = 2
        if current_round.all_matches_completed():
            menu_items[self.ROUND_MENU_FINISH] = "Mark as finished (irreversible)"
            gap = 3

        for idx, match in enumerate(current_round.matches):
            p1_data, p2_data = match
            p1, p1_score = p1_data
            p2, p2_score = p2_data

            menu_items[idx + gap] = f"{p1.full_name} vs {p2.full_name}"

        choice = cli.utils.print_menu(menu_items)
        return choice

    @staticmethod
    def display_match_infos(match):
        p1_data, p2_data = match
        p1, p1_score = p1_data
        p2, p2_score = p2_data

        cli.tournaments.print_match(p1.full_name, p2.full_name, p1_score)

    def prompt_match_menu(self, match) -> int:
        menu_items = dict()
        menu_items[self.MATCH_MENU_BACK] = "Back"

        p1_data, p2_data = match
        p1, p1_score = p1_data
        p2, p2_score = p2_data

        menu_items[self.MATCH_MENU_P1_WINS] = f"{p1.full_name} wins"
        menu_items[self.MATCH_MENU_P2_WINS] = f"{p2.full_name} wins"
        menu_items[self.MATCH_MENU_DRAW] = "Draw"

        choice = cli.utils.print_menu(menu_items)
        return choice

    def display_rounds_list(self):
        matches_per_round = len(self.tournament.competitors) // 2
        cli.tournaments.print_rounds(self.tournament.name, self.tournament.rounds, matches_per_round)

    def prepare(self):
        if self.tournament.has_competitors():
            self.populate_competitors()

        self.display_tournament_header()
        while True:
            self.display_scoreboard()
            if self.tournament.has_enough_competitors():
                should_launch = cli.tournaments.should_launch()
                if should_launch:
                    self.launch()
                    break

            self.add_new_competitor()

    # todo: check the case where there is an odd number of players
    def launch(self) -> None:
        """Creates the first round of the tournament."""
        # Sort players by elo.
        sort_players(self.tournament.competitors, PlayerSort.ELO)

        # Split the resulting list in half.
        middle_idx = len(self.tournament.competitors) // 2
        top_players = self.tournament.competitors[:middle_idx]
        bot_players = self.tournament.competitors[middle_idx:]

        # Make pairs with players of each list.
        fixtures = list(itertools.zip_longest(top_players, bot_players))

        # Add first round to the tournament.
        round_name = cli.tournaments.prompt_new_round(len(self.tournament.rounds) + 1)
        self.tournament.add_round(round_name, fixtures)
        self.tournament_registry.update_one(self.tournament)

        self.resume()

    def resume(self) -> None:
        """Resume tournament."""
        if not self.has_populated_competitors():
            self.populate_competitors()
        if not self.has_populated_rounds():
            self.populate_rounds()

        self.display_tournament_header()

        while True:
            # Main menu.
            main_menu_item = self.prompt_main_menu()

            current_round = self.tournament.last_round
            if main_menu_item == self.MAIN_MENU_SCOREBOARD:
                self.display_scoreboard()
            elif main_menu_item == self.MAIN_MENU_LIST_ROUNDS:
                self.display_rounds_list()
            elif main_menu_item == self.MAIN_MENU_CURRENT_ROUND:
                # Round menu.
                self.display_round_infos(current_round)
                round_menu_item = self.prompt_round_menu(current_round)

                if round_menu_item == self.ROUND_MENU_BACK:
                    continue
                elif round_menu_item == self.ROUND_MENU_FINISH:
                    current_round.finish()
                    # create new round
                else:
                    # Match menu.
                    while True:
                        current_match = current_round.matches[round_menu_item - (self.ROUND_MENU_BACK + 1)]
                        self.display_match_infos(current_match)
                        match_menu_item = self.prompt_match_menu(current_match)

                        if match_menu_item == self.MATCH_MENU_BACK:
                            break
                        elif match_menu_item == self.MATCH_MENU_P1_WINS:
                            self.update_match_outcome(current_match, self.MATCH_MENU_P1_WINS)
                            continue
                        elif match_menu_item == self.MATCH_MENU_P2_WINS:
                            self.update_match_outcome(current_match, self.MATCH_MENU_P2_WINS)
                            continue
                        elif match_menu_item == self.MATCH_MENU_DRAW:
                            self.update_match_outcome(current_match, self.MATCH_MENU_DRAW)
                            continue




@app.command()
def init(db_path: str = typer.Option(
    str(DEFAULT_DB_LOCATION),
    "--db-path",
    "-db",
    prompt="chesstournament database location?")):
    """Initialize chess tournament local storage."""
    app_init_error = config.init_app(db_path)
    if app_init_error:
        cli.utils.print_error(f"Failed to create config file:\n'{ERRORS[app_init_error]}'")
        raise typer.Exit(1)

    db_init_error = create_database(Path(db_path))
    if db_init_error:
        cli.utils.print_error(f"Failed to create database file:\n'{ERRORS[db_init_error]}'", )
        raise typer.Exit(1)
    else:
        cli.utils.print_success(f"Succeed to create local storage file:\n'{db_path}'")


@app.command()
def run(tournament_id: int = typer.Option(
    ...,
    "--tournament",
    "-t",
    help="A tournament id.")):
    """Run an existing tournament interactively."""
    try:
        tournament_registry = tournaments.get_tournaments_registry()
        players_registry = players.get_players_registry()
        tournament = tournament_registry.get_by_id(tournament_id)
        tournament_engine = TournamentEngine(tournament, players_registry, tournament_registry)

        if tournament.has_started():
            tournament_engine.resume()
        else:
            tournament_engine.prepare()

    except (TournamentException, PlayerException, DatabaseException, TournamentEngineException) as error:
        cli.utils.print_error(f"\nTournament execution failed:\n{error.message}")
        raise typer.Exit(1)


def version_callback(value: bool):
    if value:
        cli.utils.print_raw(f"{__app_name__} version: {__version__}")
        raise typer.Exit()
    return None


@app.callback()
def main(
        verbose: Optional[bool] = typer.Option(
            None,
            "--version",
            "-v",
            help="Show the application's version and exit.",
            callback=version_callback,
            is_eager=True
        )):
    """
    A CLI app to manage chess tournaments.
    """
    return None
