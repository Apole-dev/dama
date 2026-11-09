from dataclasses import dataclass


SIZE = 8
RED = "red"
WHITE = "white"
Position = tuple[int, int]


@dataclass(frozen=True)
class Move:
    start: Position
    path: tuple[Position, ...]
    captures: tuple[Position, ...] = ()

    @property
    def end(self) -> Position:
        return self.path[-1]


class Game:
    def __init__(self, board: list[list[str | None]] | None = None, turn: str = RED):
        self.board = [row[:] for row in board] if board is not None else self._initial_board()
        self.turn = turn
        self.winner: str | None = None
        self.history: list[tuple[list[list[str | None]], str]] = []
        self._update_winner()

    @staticmethod
    def _initial_board() -> list[list[str | None]]:
        board: list[list[str | None]] = [[None for _ in range(SIZE)] for _ in range(SIZE)]
        for row in range(SIZE):
            if row not in (0, 1, 2, 5, 6, 7):
                continue
            for col in range(SIZE):
                if (row + col) % 2 == 1:
                    board[row][col] = "w" if row < 3 else "r"
        return board

    @staticmethod
    def _inside(row: int, col: int) -> bool:
        return 0 <= row < SIZE and 0 <= col < SIZE

    @staticmethod
    def _owner(piece: str) -> str:
        return RED if piece.lower() == "r" else WHITE

    @staticmethod
    def _directions(piece: str) -> tuple[Position, ...]:
        if piece.isupper():
            return ((-1, -1), (-1, 1), (1, -1), (1, 1))
        direction = -1 if piece == "r" else 1
        return ((direction, -1), (direction, 1))

    @staticmethod
    def _crown_row(piece: str) -> int:
        return 0 if piece.lower() == "r" else SIZE - 1

    def _captures_from(
        self,
        board: list[list[str | None]],
        start: Position,
        current: Position,
        piece: str,
        path: tuple[Position, ...],
        captured: tuple[Position, ...],
    ) -> list[Move]:
        moves: list[Move] = []
        row, col = current
        for dr, dc in self._directions(piece):
            middle = (row + dr, col + dc)
            end = (row + 2 * dr, col + 2 * dc)
            # Captured pieces stay blocked until the jump chain ends.
            if not self._inside(*end) or middle in captured:
                continue
            target = board[middle[0]][middle[1]]
            if target is None or self._owner(target) == self._owner(piece):
                continue
            if board[end[0]][end[1]] is not None:
                continue
            next_path = path + (end,)
            next_captured = captured + (middle,)
            # Crowning ends the move.
            if not piece.isupper() and end[0] == self._crown_row(piece):
                moves.append(Move(start, next_path, next_captured))
                continue
            next_board = [line[:] for line in board]
            next_board[row][col] = None
            next_board[end[0]][end[1]] = piece
            continuations = self._captures_from(
                next_board, start, end, piece, next_path, next_captured
            )
            moves.extend(continuations or [Move(start, next_path, next_captured)])
        return moves

    def legal_moves(self) -> list[Move]:
        if self.winner is not None:
            return []
        captures: list[Move] = []
        slides: list[Move] = []
        for row in range(SIZE):
            for col in range(SIZE):
                piece = self.board[row][col]
                if piece is None or self._owner(piece) != self.turn:
                    continue
                start = (row, col)
                captures.extend(self._captures_from(self.board, start, start, piece, (), ()))
                for dr, dc in self._directions(piece):
                    end = (row + dr, col + dc)
                    if self._inside(*end) and self.board[end[0]][end[1]] is None:
                        slides.append(Move(start, (end,)))
        return captures if captures else slides

    def play(self, move: Move) -> None:
        if move not in self.legal_moves():
            raise ValueError("Illegal move")
        self.history.append(([row[:] for row in self.board], self.turn))
        row, col = move.start
        piece = self.board[row][col]
        assert piece is not None
        self.board[row][col] = None
        for captured_row, captured_col in move.captures:
            self.board[captured_row][captured_col] = None
        end_row, end_col = move.end
        if end_row == self._crown_row(piece):
            piece = piece.upper()
        self.board[end_row][end_col] = piece
        self.turn = WHITE if self.turn == RED else RED
        self._update_winner()

    def undo(self) -> bool:
        if not self.history:
            return False
        self.board, self.turn = self.history.pop()
        self._update_winner()
        return True

    def _update_winner(self) -> None:
        self.winner = None
        if not self.legal_moves():
            self.winner = WHITE if self.turn == RED else RED
