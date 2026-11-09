import queue
import threading
import tkinter as tk

from computer import choose_move
from dama import Game, Move, RED, SIZE, WHITE


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
        self.screen = "menu"
        self.mode = "local"
        self.difficulty = "normal"
        self.ai_generation = 0
        self.ai_thinking = False
        self.ai_results: queue.SimpleQueue[tuple[int, Move | Exception]] = queue.SimpleQueue()
        self.ai_error = False
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
        self.root.bind("<Control-n>", lambda event: self.new_game() if self.screen == "game" else None)
        self.draw()

    def start_game(self, mode: str) -> None:
        self.mode = mode
        self.screen = "game"
        self.new_game()

    def show_menu(self) -> None:
        self.ai_generation += 1
        self.ai_thinking = False
        self.ai_error = False
        self.screen = "menu"
        self.clear_selection()
        self.draw()

    def new_game(self) -> None:
        self.ai_generation += 1
        self.ai_thinking = False
        self.ai_error = False
        self.game = Game()
        self.last_move = None
        self.clear_selection()
        self.draw()

    def undo(self) -> None:
        if self.screen != "game":
            return
        self.ai_generation += 1
        self.ai_thinking = False
        self.ai_error = False
        if self.preview is not None:
            self.clear_selection()
        elif self.game.undo():
            if self.mode == "computer" and self.game.turn == WHITE:
                self.game.undo()
            self.last_move = None
            self.clear_selection()
        self.draw()

    def clear_selection(self) -> None:
        self.selected = None
        self.candidates = []
        self.step_index = 0
        self.preview = None

    def on_click(self, event: tk.Event) -> None:
        if self.screen == "menu":
            self.click_menu(event.x, event.y)
            return
        col = (event.x - MARGIN) // CELL
        row = (event.y - MARGIN) // CELL
        if 0 <= row < SIZE and 0 <= col < SIZE:
            self.choose_square((row, col))
            return
        x = BOARD_SIZE + 2 * MARGIN + 20
        if x <= event.x <= x + PANEL_WIDTH - 40:
            if 300 <= event.y <= 342:
                self.new_game()
            elif 354 <= event.y <= 396:
                self.undo()
            elif 408 <= event.y <= 450:
                self.show_menu()

    def click_menu(self, x: int, y: int) -> None:
        if 194 <= x <= 590 and 190 <= y <= 260:
            self.start_game("local")
        elif 194 <= x <= 590 and 276 <= y <= 346:
            self.start_game("computer")
        elif 406 <= y <= 452:
            for name, left, right in (("easy", 194, 316), ("normal", 328, 450), ("hard", 462, 584)):
                if left <= x <= right:
                    self.difficulty = name
                    self.draw()
                    break

    def choose_square(self, square: tuple[int, int]) -> None:
        if self.game.winner is not None or self.ai_thinking:
            return
        if self.mode == "computer" and self.game.turn == WHITE:
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
            if self.mode == "computer" and self.game.winner is None:
                self.start_computer_turn()

    def start_computer_turn(self) -> None:
        self.ai_thinking = True
        generation = self.ai_generation
        snapshot = Game(self.game.board, self.game.turn)

        def worker() -> None:
            try:
                result = choose_move(snapshot, self.difficulty)
            except Exception as error:
                result = error
            self.ai_results.put((generation, result))

        threading.Thread(target=worker, daemon=True).start()
        self.root.after(80, lambda: self.poll_computer(generation))

    def poll_computer(self, generation: int) -> None:
        if generation != self.ai_generation or self.screen != "game":
            return
        while True:
            try:
                result_generation, result = self.ai_results.get_nowait()
            except queue.Empty:
                self.root.after(80, lambda: self.poll_computer(generation))
                return
            if result_generation != generation:
                continue
            self.ai_thinking = False
            if isinstance(result, Exception):
                self.ai_error = True
                self.draw()
                return
            self.game.play(result)
            self.last_move = result
            self.draw()
            return

    def draw(self) -> None:
        self.canvas.delete("all")
        if self.screen == "menu":
            self.draw_menu()
            return
        self.draw_board()
        self.draw_panel()

    def draw_menu(self) -> None:
        self.canvas.create_rectangle(0, 0, 784, 572, fill=BACKGROUND, outline="")
        self.canvas.create_text(
            392, 103, text="DAMA", fill="#f4dfb9",
            font=("DejaVu Sans", 46, "bold")
        )
        self.canvas.create_line(318, 153, 466, 153, fill="#b95b47", width=3)
        self.draw_menu_card(194, 190, "İki oyuncu")
        self.draw_menu_card(194, 276, "Bilgisayara karşı")
        self.canvas.create_text(
            194, 382, anchor="nw", text="SEVİYE", fill="#a99983",
            font=("DejaVu Sans", 10, "bold")
        )
        labels = (("easy", "Kolay", 194), ("normal", "Orta", 328), ("hard", "Zor", 462))
        for value, label, x in labels:
            active = value == self.difficulty
            self.canvas.create_rectangle(
                x, 406, x + 122, 452,
                fill="#95553e" if active else "#302620",
                outline="#be8160" if active else "#665044", width=2
            )
            self.canvas.create_text(
                x + 61, 429, text=label,
                fill="#fff0d2" if active else "#a99983",
                font=("DejaVu Sans", 12, "bold")
            )

    def draw_menu_card(self, x: int, y: int, title: str) -> None:
        self.canvas.create_rectangle(
            x, y, x + 396, y + 70, fill="#342722", outline="#8e684d", width=2
        )
        self.canvas.create_text(
            x + 198, y + 35, text=title,
            fill="#f6dfba", font=("DejaVu Sans", 17, "bold")
        )

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
            if self.selected is None and not self.ai_thinking else set()
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
        elif self.ai_error:
            status = "Motor açılamadı"
        elif self.ai_thinking:
            status = "Bilgisayar düşünüyor"
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
            x, 183, anchor="nw", text=f"Kırmızı  {red_count}",
            fill="#e8c5b8", font=("DejaVu Sans", 13)
        )
        self.canvas.create_text(
            x, 213, anchor="nw", text=f"Beyaz    {white_count}",
            fill="#f0e7d5", font=("DejaVu Sans", 13)
        )
        self.draw_button(x, 300, "Yeni oyun", True)
        self.draw_button(x, 354, "Geri al", self.preview is not None or bool(self.game.history))
        self.draw_button(x, 408, "Menü", True)

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
