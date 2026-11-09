from dama import Game, Move, WHITE


def square_number(row: int, col: int) -> int:
    return row * 4 + col // 2 + 1


def position(index: int) -> tuple[int, int]:
    row, offset = divmod(index, 4)
    return row, offset * 2 + (1 if row % 2 == 0 else 0)


def to_fen(game: Game) -> str:
    red: list[str] = []
    white: list[str] = []
    for row, cells in enumerate(game.board):
        for col, piece in enumerate(cells):
            if piece is None:
                continue
            number = square_number(row, col)
            entry = f"K{number}" if piece.isupper() else str(number)
            (red if piece.lower() == "r" else white).append(entry)
    turn = "W" if game.turn != WHITE else "B"
    return f"{turn}:W{','.join(red)}:B{','.join(white)}"


def choose_move(game: Game, difficulty: str = "normal") -> Move:
    from draughts import AmericanBoard, SimpleEngine

    if game.turn != WHITE or game.winner is not None:
        raise ValueError("Computer cannot move")

    class ForcedCaptureBoard(AmericanBoard):
        @property
        def legal_moves(self):
            moves = super().legal_moves
            captures = [move for move in moves if move.captured_list]
            return captures or moves

    levels = {"easy": (2, 0.25), "normal": (4, 0.8), "hard": (6, 1.5)}
    depth, seconds = levels[difficulty]
    board = ForcedCaptureBoard.from_fen(to_fen(game))
    engine = SimpleEngine(depth_limit=depth, time_limit=seconds)
    selected = engine.get_best_move(board)
    squares = selected.square_list
    move = Move(
        position(squares[0]),
        tuple(position(index) for index in squares[1:]),
        tuple(position(index) for index in selected.captured_list),
    )
    if move not in game.legal_moves():
        raise ValueError("Engine returned an illegal move")
    return move
