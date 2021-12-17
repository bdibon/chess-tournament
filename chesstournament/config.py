"""This module provides the chess-tournament config functionality."""

from configparser import ConfigParser
from pathlib import Path

import typer

from chesstournament import __app_name__, DIR_ERROR, FILE_ERROR, SUCCESS

CONFIG_DIR_PATH = Path(typer.get_app_dir(__app_name__))
CONFIG_FILE_PATH = CONFIG_DIR_PATH / "config.ini"


def init_app(db_path: str) -> int:
    """Initialize the application."""
    config_code = _create_config_file()
    if config_code != SUCCESS:
        return config_code

    db_path_code = _set_database_path(db_path)
    if db_path_code != SUCCESS:
        return db_path_code

    return SUCCESS


def get_database_path() -> Path:
    """Read database path from configuration file."""
    if CONFIG_FILE_PATH.exists():
        config_parser = ConfigParser()
        config_parser.read(CONFIG_FILE_PATH)
        return Path(config_parser['General']['database'])
    else:
        raise Exception(FILE_ERROR)


def _create_config_file() -> int:
    """Create the configuration file."""
    try:
        CONFIG_DIR_PATH.mkdir(exist_ok=True)
    except OSError:
        return DIR_ERROR
    try:
        CONFIG_FILE_PATH.touch(exist_ok=True)
    except OSError:
        return FILE_ERROR

    return SUCCESS


def _set_database_path(db_path: str) -> int:
    """Set the database path in the config file."""
    config_parser = ConfigParser()
    config_parser['General'] = {'database': db_path}

    try:
        with CONFIG_FILE_PATH.open("w") as file:
            config_parser.write(file)
    except OSError:
        return FILE_ERROR

    return SUCCESS
