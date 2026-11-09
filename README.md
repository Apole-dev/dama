# Dama

Two player checkers game based on the supplied board image.

## Run

```sh
python3 dama.py
```

Choose a move by its number. Enter `q` to quit.

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
