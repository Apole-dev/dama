import tkinter as tk

from dama import Game, Move, RED, SIZE


CELL = 68
MARGIN = 14
BOARD_SIZE = CELL * SIZE
PANEL_WIDTH = 212
LIGHT = "#edcf9c"
DARK = "#855336"
FRAME = "#4b2e21"
BACKGROUND = "#241b18"
ACCENT = "#e7bc67"


class DamaWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Dama")
        self.root.configure(bg=BACKGROUND)
        self.root.resizable(False, False)
        self.game = Game()
        self.selected: tuple[int, int] | None = None
        self.candidates: list[Move] = []
        self.step_index = 0
        self.preview: list[list[str | None]] | None = None
        self.last_move: Move | None = None

        width = BOARD_SIZE + 2 * MARGIN + PANEL_WIDTH
        height = BOARD_SIZE + 2 * MARGIN
        self.canvas = tk.Canvas(
            root, width=width, height=height, bg=BACKGROUND,
            highlightthickness=0, cursor="hand2"
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)
        self.root.bind("<Control-z>", lambda event: self.undo())
        self.root.bind("<Control-n>", lambda event: self.new_game())
        self.draw()

    def new_game(self) -> None:
        self.game = Game()
        self.last_move = None
        self.clear_selection()
        self.draw()

    def undo(self) -> None:
        if self.preview is not None:
            self.clear_selection()
        elif self.game.undo():
            self.last_move = None
            self.clear_selection()
        self.draw()

    def clear_selection(self) -> None:
        self.selected = None
        self.candidates = []
        self.step_index = 0
        self.preview = None

    def on_click(self, event: tk.Event) -> None:
        col = (event.x - MARGIN) // CELL
        row = (event.y - MARGIN) // CELL
        if 0 <= row < SIZE and 0 <= col < SIZE:
            self.choose_square((row, col))
            return
        x = BOARD_SIZE + 2 * MARGIN + 20
        if x <= event.x <= x + PANEL_WIDTH - 40:
            if 372 <= event.y <= 414:
                self.new_game()
            elif 426 <= event.y <= 468:
                self.undo()

    def choose_square(self, square: tuple[int, int]) -> None:
        if self.game.winner is not None:
            return
        moves = self.game.legal_moves()
        if self.selected is None:
            self.select_piece(square, moves)
        elif self.step_index == 0 and square == self.selected:
            self.clear_selection()
        else:
            matching = [
                move for move in self.candidates
                if move.path[self.step_index] == square
            ]
            if matching:
                self.take_step(square, matching)
            elif self.step_index == 0:
                self.select_piece(square, moves)
        self.draw()

    def select_piece(self, square: tuple[int, int], moves: list[Move]) -> None:
        self.clear_selection()
        self.candidates = [move for move in moves if move.start == square]
        if self.candidates:
            self.selected = square

    def take_step(self, square: tuple[int, int], matching: list[Move]) -> None:
        if self.preview is None:
            self.preview = [row[:] for row in self.game.board]
        assert self.selected is not None
        piece = self.preview[self.selected[0]][self.selected[1]]
        self.preview[self.selected[0]][self.selected[1]] = None
        self.preview[square[0]][square[1]] = piece
        if matching[0].captures:
            captured = matching[0].captures[self.step_index]
            self.preview[captured[0]][captured[1]] = None
        self.selected = square
        self.candidates = matching
        self.step_index += 1
        completed = [move for move in matching if len(move.path) == self.step_index]
        if completed:
            move = completed[0]
            self.game.play(move)
            self.last_move = move
            self.clear_selection()

    def draw(self) -> None:
        self.canvas.delete("all")
        self.draw_board()
        self.draw_panel()

    def draw_board(self) -> None:
        x0 = MARGIN
        y0 = MARGIN
        self.canvas.create_rectangle(
            x0 - 7, y0 - 7, x0 + BOARD_SIZE + 7, y0 + BOARD_SIZE + 7,
            fill=FRAME, outline="#b88a56", width=3
        )
        board = self.preview if self.preview is not None else self.game.board
        destinations = (
            {move.path[self.step_index] for move in self.candidates}
            if self.candidates else set()
        )
        selectable = (
            {move.start for move in self.game.legal_moves()}
            if self.selected is None else set()
        )
        for row in range(SIZE):
            for col in range(SIZE):
                x1 = x0 + col * CELL
                y1 = y0 + row * CELL
                x2 = x1 + CELL
                y2 = y1 + CELL
                square = (row, col)
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=DARK if (row + col) % 2 else LIGHT,
                    outline="#71482f", width=1
                )
                if self.last_move and square in (self.last_move.start, self.last_move.end):
                    self.canvas.create_rectangle(
                        x1 + 4, y1 + 4, x2 - 4, y2 - 4,
                        outline="#ebc86e", width=3
                    )
                if square == self.selected:
                    self.canvas.create_rectangle(
                        x1 + 4, y1 + 4, x2 - 4, y2 - 4,
                        outline="#ffe69b", width=4
                    )
                if square in destinations:
                    self.canvas.create_oval(
                        x1 + 29, y1 + 29, x2 - 29, y2 - 29,
                        fill="#d5e7a2", outline="#547b47", width=2
                    )
                piece = board[row][col]
                if piece:
                    self.draw_piece(x1, y1, piece, square in selectable)

    def draw_piece(self, x: int, y: int, piece: str, selectable: bool) -> None:
        red = piece.lower() == "r"
        outer = "#7b171c" if red else "#918675"
        face = "#c6383b" if red else "#f0e7d5"
        inner = "#a8282c" if red else "#d8ceba"
        self.canvas.create_oval(
            x + 12, y + 16, x + CELL - 9, y + CELL - 7,
            fill="#3b2b23", outline=""
        )
        self.canvas.create_oval(
            x + 10, y + 10, x + CELL - 10, y + CELL - 10,
            fill=outer, outline="#3b2924", width=2
        )
        self.canvas.create_oval(
            x + 15, y + 14, x + CELL - 15, y + CELL - 17,
            fill=face, outline="#f49b92" if red else "#fff9ea", width=2
        )
        self.canvas.create_oval(
            x + 24, y + 23, x + CELL - 24, y + CELL - 25,
            fill=inner, outline=outer, width=2
        )
        if piece.isupper():
            self.canvas.create_text(
                x + CELL // 2, y + CELL // 2 - 1,
                text="♛", fill="#f7d77b" if red else "#76562c",
                font=("DejaVu Sans", 24, "bold")
            )
        elif selectable:
            self.canvas.create_oval(
                x + 4, y + 4, x + CELL - 4, y + CELL - 4,
                outline="#e7d380", width=2
            )

    def draw_panel(self) -> None:
        x = BOARD_SIZE + 2 * MARGIN + 20
        self.canvas.create_text(
            x, 45, anchor="nw", text="DAMA", fill="#f5dfb3",
            font=("DejaVu Sans", 26, "bold")
        )
        self.canvas.create_line(x, 91, x + 170, 91, fill="#8e6d4e", width=2)
        if self.game.winner:
            status = "Kırmızı kazandı" if self.game.winner == RED else "Beyaz kazandı"
        elif self.preview is not None:
            status = "Almaya devam et"
        else:
            status = "Kırmızı oynuyor" if self.game.turn == RED else "Beyaz oynuyor"
        self.canvas.create_text(
            x, 117, anchor="nw", text=status, fill=ACCENT,
            font=("DejaVu Sans", 14, "bold")
        )
        board = self.preview if self.preview is not None else self.game.board
        red_count = sum(piece is not None and piece.lower() == "r"
                        for row in board for piece in row)
        white_count = sum(piece is not None and piece.lower() == "w"
                          for row in board for piece in row)
        self.canvas.create_text(
            x, 161, anchor="nw", text=f"Kırmızı  {red_count}",
            fill="#e8c5b8", font=("DejaVu Sans", 13)
        )
        self.canvas.create_text(
            x, 188, anchor="nw", text=f"Beyaz    {white_count}",
            fill="#f0e7d5", font=("DejaVu Sans", 13)
        )
        tips = ("Taşı seç.", "İşaretli kareye tıkla.", "Alma varsa zorunludur.")
        for index, tip in enumerate(tips):
            self.canvas.create_text(
                x, 265 + index * 27, anchor="nw", text=tip,
                fill="#cbb8a1", font=("DejaVu Sans", 11)
            )
        self.draw_button(x, 372, "Yeni oyun", True)
        self.draw_button(x, 426, "Geri al", self.preview is not None or bool(self.game.history))
        self.canvas.create_text(
            x, 493, anchor="nw", text="Ctrl N  Yeni oyun\nCtrl Z  Geri al",
            fill="#a9947c", font=("DejaVu Sans", 10)
        )

    def draw_button(self, x: int, y: int, label: str, enabled: bool) -> None:
        self.canvas.create_rectangle(
            x, y, x + PANEL_WIDTH - 40, y + 42,
            fill="#a4744d" if enabled else "#514139",
            outline="#d7ad76" if enabled else "#76655a", width=2
        )
        self.canvas.create_text(
            x + (PANEL_WIDTH - 40) // 2, y + 21, text=label,
            fill="#fff0cf" if enabled else "#98897d",
            font=("DejaVu Sans", 12, "bold")
        )


def main() -> None:
    root = tk.Tk()
    DamaWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
