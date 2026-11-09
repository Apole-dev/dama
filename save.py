import json
from pathlib import Path

from dama import Game, Move


SAVE_PATH = Path.home() / ".local" / "share" / "dama" / "game.json"


def save_game(moves: list[Move], mode: str, difficulty: str, theme: str) -> None:
    data = {
        "version": 1,
        "mode": mode,
        "difficulty": difficulty,
        "theme": theme,
        "moves": [
            {"start": move.start, "path": move.path, "captures": move.captures}
            for move in moves
        ],
    }
    SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary = SAVE_PATH.with_suffix(".tmp")
    temporary.write_text(json.dumps(data), encoding="utf-8")
    temporary.replace(SAVE_PATH)


def load_game() -> tuple[Game, list[Move], str, str, str] | None:
    try:
        data = json.loads(SAVE_PATH.read_text(encoding="utf-8"))
        if data["version"] != 1 or data["mode"] not in ("local", "computer"):
            return None
        if data["difficulty"] not in ("easy", "normal", "hard"):
            return None
        if data["theme"] not in ("classic", "slate"):
            return None
        game = Game()
        moves = []
        for item in data["moves"]:
            move = Move(
                tuple(item["start"]),
                tuple(tuple(square) for square in item["path"]),
                tuple(tuple(square) for square in item["captures"]),
            )
            game.play(move)
            moves.append(move)
        return game, moves, data["mode"], data["difficulty"], data["theme"]
    except (OSError, KeyError, TypeError, ValueError, IndexError):
        return None
