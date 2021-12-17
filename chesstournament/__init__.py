"""This is the top level package for chess-tournament."""

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
    DB_READ_ERROR: "database read error",
    DB_WRITE_ERROR: "database write error",
    DIR_ERROR: "config directory error",
    FILE_ERROR: "config file error"
}