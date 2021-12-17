"""This is the top level package for chess-tournament."""

__app_name__ = "chess-tournament"
__version__ = "0.1.0"

(SUCCESS, DB_WRITE_ERROR) = range(2)

ERRORS = {
    DB_WRITE_ERROR: "database write error"
}