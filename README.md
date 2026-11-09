# Dama

Two player checkers game based on the supplied board image. The game uses Python and Tkinter.

## Run

```sh
./run.sh
```

The first run downloads the `py-draughts` package into `.venv`. Later runs use the installed package. This is a ready game engine, not a neural network model.

Choose two players or play against the computer from the start screen. Computer levels are easy, normal, and hard. The computer uses the downloaded `py-draughts` engine. It does not need internet access during play.

Select a piece, then click a marked square. For a capture chain, click each landing square. Use the buttons to start a new game, undo a move, or return to the menu. Ctrl N and Ctrl Z are keyboard shortcuts.

The terminal version is available with `python3 cli.py`.

The computer engine comes from [py-draughts](https://github.com/miskibin/py-draughts), licensed under GPL-3.0.

## Files

- `dama.py` contains the rules and game state.
- `computer.py` connects the downloaded engine to the game.
- `ui.py` handles input and animation.
- `render.py` draws the menu and board.
- `cli.py` runs the terminal version.

## Rules

- Red moves first. Each player starts with 12 pieces on dark squares.
- Men move and capture one diagonal step forward. Kings move and capture one diagonal step in either direction.
- Captures are required. A capture chain continues while another jump is available. Any available capture route may be chosen.
- A man becomes a king on the far row. Crowning ends the move.
- A player wins when the opponent has no legal move.

## Test

```sh
.venv/bin/python -m unittest -v
```
