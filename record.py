from dama import Game, Move, RED, WHITE


def square_name(square: tuple[int, int]) -> str:
    row, col = square
    return f"{chr(97 + col)}{8 - row}"


def move_text(move: Move) -> str:
    separator = "x" if move.captures else "-"
    return separator.join(square_name(square) for square in (move.start,) + move.path)


def export_pdn(game: Game, moves: list[Move]) -> str:
    result = "0-1" if game.winner == RED else "1-0" if game.winner == WHITE else (
        "1/2-1/2" if game.draw_reason else "*"
    )
    lines = ['[GameType "21,B,8,8,A0,0"]', '[Black "Kırmızı"]',
             '[White "Beyaz"]', f'[Result "{result}"]', ""]
    turns = [
        f"{index // 2 + 1}. {move_text(moves[index])} "
        + (move_text(moves[index + 1]) if index + 1 < len(moves) else "")
        for index in range(0, len(moves), 2)
    ]
    lines.extend(turns)
    lines.append(result)
    return "\n".join(lines) + "\n"
