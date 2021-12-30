# chess-tournament

This project provides a command line interface (CLI) application to manage chess tournaments with the [Swiss-system format](https://en.wikipedia.org/wiki/Swiss-system_tournament).

## Setup

Clone the project repository.

```
git clone git@github.com:bdibon/chess-tournament.git
```

Create a virtual environment and activate it.

```
python -m venv venv
source venv/bin/activate
```

Install the required dependencies.

```
pip install -r requirements.txt
```

There is one final step though, configure the local storage of the data.

```
python -m chesstournament init
```

Now the app should run properly!

```
> python -m chesstournament --help

Usage: python -m chesstournament [OPTIONS] COMMAND [ARGS]...

  A CLI app to manage chess tournaments.

Options:
  -v, --version  Show the application's version and exit.
  --help         Show this message and exit.

Commands:
  init         Initialize chess tournament local storage.
  players      Manage players in the app.
  run          Run an existing tournament interactively.
  tournaments  Manage tournaments in the app
```

## Manage players

After setting up the application, the next logical step is to add players to your local storage, this is done via the `players` command.

```
> python -m chesstournament players --help

Usage: python -m chesstournament players [OPTIONS] COMMAND [ARGS]...

  Manage players in the app.

Options:
  --help  Show this message and exit.

Commands:
  add     Add a new player to the database.
  list    List saved players, sorted by id (default).
  update  Update a player in the local database.
```

The `players` subcommands are explicit enough and should output the relevant instructions to their usage.

## Manage tournaments

Once you have enough players in your local storage to start a tournament (by default it's 2), it is time to create a new tournament! This is akin to add players, just run `python -m chesstournament tournaments add` and the application will ask you the relevant information.

## Run a tournament

This is what the app is made for! Once you have created your tournament you can run it interactively with the `run` command, note you have to provide the tournament's id with the `-t` flag.

```
python -m chesstournament run -t 1
```

## Generate a new flake8 report

This project uses flake8 to enforce a good python code style, whenever you update the code you can check for eventual *violations*.

```
python -m flake8
```
