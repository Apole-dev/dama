# Dama

Two player checkers game based on the supplied board image. The game uses Python and Tkinter.

## Run

```sh
python3 ui.py
```

Select a piece, then click a marked square. For a capture chain, click each landing square. Use the buttons to start a new game or undo a move. Ctrl N and Ctrl Z are keyboard shortcuts.

The terminal version is available with `python3 dama.py`.

## Rules

- Red moves first. Each player starts with 12 pieces on dark squares.
- Men move and capture one diagonal step forward. Kings move and capture one diagonal step in either direction.
- Captures are required. A capture chain continues while another jump is available. Any available capture route may be chosen.
- A man becomes a king on the far row. Crowning ends the move.
- A player wins when the opponent has no legal move.

## Test

```sh
python3 -m unittest -v
```
