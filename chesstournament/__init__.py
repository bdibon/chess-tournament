"""This is the top level package for chess-tournament."""

from chesstournament.views.cli import CLIView

__app_name__ = "chesstournament"
__version__ = "0.1.0"

(
    SUCCESS,
    DB_READ_ERROR,
    DB_WRITE_ERROR,
    DIR_ERROR,
    FILE_ERROR
) = range(5)

ERRORS = {
    DB_READ_ERROR: "Database read error.",
    DB_WRITE_ERROR: "Database write error.",
    DIR_ERROR: "Config directory error.",
    FILE_ERROR: "Config file error."
}

view = CLIView()
