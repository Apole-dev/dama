import queue
import threading
import tkinter as tk

from computer import choose_move
from dama import Game, Move, SIZE, WHITE
from render import BACKGROUND, BOARD_SIZE, CELL, MARGIN, PANEL_WIDTH, GameRenderer
from save import load_game, save_game


ANIMATION_FRAMES = 12
ANIMATION_DELAY_MS = 32
STEP_PAUSE_MS = 700


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
        self.theme = "classic"
        self.saved_game = load_game()
        if self.saved_game is not None and self.saved_game[0].winner is not None:
            self.saved_game = None
        if self.saved_game is not None:
            self.theme = self.saved_game[4]
        self.moves: list[Move] = []
        self.ai_generation = 0
        self.ai_thinking = False
        self.ai_results: queue.SimpleQueue[tuple[int, Move | Exception]] = queue.SimpleQueue()
        self.ai_error = False
        self.selected: tuple[int, int] | None = None
        self.candidates: list[Move] = []
        self.step_index = 0
        self.preview: list[list[str | None]] | None = None
        self.last_move: Move | None = None
        self.ai_move: Move | None = None
        self.ai_step = 0
        self.animated_piece: tuple[str, float, float] | None = None

        width = BOARD_SIZE + 2 * MARGIN + PANEL_WIDTH
        height = BOARD_SIZE + 2 * MARGIN
        self.canvas = tk.Canvas(
            root, width=width, height=height, bg=BACKGROUND,
            highlightthickness=0, cursor="hand2"
        )
        self.canvas.pack()
        self.renderer = GameRenderer(self.canvas, self)
        self.canvas.bind("<Button-1>", self.on_click)
        self.root.bind("<Control-z>", lambda event: self.undo())
        self.root.bind("<Control-n>", lambda event: self.new_game() if self.screen == "game" else None)
        self.draw()

    def start_game(self, mode: str) -> None:
        self.mode = mode
        self.screen = "game"
        self.new_game()

    def continue_game(self) -> None:
        saved = load_game()
        if saved is None or saved[0].winner is not None:
            self.saved_game = None
            self.draw()
            return
        self.ai_generation += 1
        self.game, self.moves, self.mode, self.difficulty, self.theme = saved
        self.saved_game = saved
        self.screen = "game"
        self.ai_thinking = False
        self.ai_error = False
        self.last_move = self.moves[-1] if self.moves else None
        self.clear_selection()
        self.draw()
        if self.mode == "computer" and self.game.turn == WHITE and self.game.winner is None:
            self.start_computer_turn()

    def persist(self) -> None:
        save_game(self.moves, self.mode, self.difficulty, self.theme)
        self.saved_game = None if self.game.winner is not None else (
            self.game, self.moves, self.mode, self.difficulty, self.theme
        )

    def show_menu(self) -> None:
        self.ai_generation += 1
        self.ai_thinking = False
        self.ai_error = False
        self.screen = "menu"
        self.clear_selection()
        self.saved_game = load_game()
        if self.saved_game is not None and self.saved_game[0].winner is not None:
            self.saved_game = None
        self.draw()

    def new_game(self) -> None:
        self.ai_generation += 1
        self.ai_thinking = False
        self.ai_error = False
        self.game = Game()
        self.moves = []
        self.last_move = None
        self.clear_selection()
        self.persist()
        self.draw()

    def undo(self) -> None:
        if self.screen != "game":
            return
        was_computer_turn = self.ai_thinking and self.mode == "computer"
        self.ai_generation += 1
        self.ai_thinking = False
        self.ai_error = False
        if was_computer_turn:
            # Undo the human move when a computer turn is pending.
            self.clear_selection()
            self.game.undo()
            self.moves.pop()
        elif self.preview is not None:
            self.clear_selection()
        elif self.game.undo():
            self.moves.pop()
            if self.mode == "computer" and self.game.turn == WHITE:
                if self.game.undo():
                    self.moves.pop()
            self.clear_selection()
        self.last_move = self.moves[-1] if self.moves else None
        self.persist()
        self.draw()

    def clear_selection(self) -> None:
        self.selected = None
        self.candidates = []
        self.step_index = 0
        self.preview = None
        self.ai_move = None
        self.ai_step = 0
        self.animated_piece = None

    def on_click(self, event: tk.Event) -> None:
        if self.screen == "menu":
            self.click_menu(event.x, event.y)
            return
        if self.game.winner is not None and 198 <= event.x <= 370:
            if 307 <= event.y <= 351:
                self.new_game()
                return
            if 361 <= event.y <= 405:
                self.show_menu()
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
            elif 464 <= event.y <= 558:
                self.show_history()

    def show_history(self) -> None:
        window = tk.Toplevel(self.root)
        window.title("Hamleler")
        window.geometry("300x400")
        frame = tk.Frame(window)
        frame.pack(fill="both", expand=True, padx=12, pady=12)
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")
        history = tk.Listbox(frame, font=("DejaVu Sans", 11), yscrollcommand=scrollbar.set)
        history.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=history.yview)
        for index, move in enumerate(self.moves, 1):
            side = "Kırmızı" if index % 2 else "Beyaz"
            squares = (move.start,) + move.path
            separator = " x " if move.captures else " - "
            notation = separator.join(f"{chr(97 + col)}{8 - row}" for row, col in squares)
            history.insert("end", f"{index}. {side}  {notation}")
        history.yview_moveto(1)

    def click_menu(self, x: int, y: int) -> None:
        if 52 <= x <= 448 and 205 <= y <= 275:
            self.start_game("local")
        elif 52 <= x <= 448 and 291 <= y <= 361:
            self.start_game("computer")
        elif self.saved_game is not None and 503 <= x <= 735 and 410 <= y <= 454:
            self.continue_game()
        elif 503 <= x <= 735 and 474 <= y <= 518:
            self.theme = "slate" if self.theme == "classic" else "classic"
            self.draw()
        elif 426 <= y <= 472:
            for name, left, right in (("easy", 52, 174), ("normal", 186, 308), ("hard", 320, 442)):
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
            self.moves.append(move)
            self.last_move = move
            self.clear_selection()
            self.persist()
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
        # Ignore results from canceled turns.
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
            if isinstance(result, Exception):
                self.ai_thinking = False
                self.ai_error = True
                self.draw()
                return
            self.ai_move = result
            self.ai_step = 0
            # Keep the game unchanged until the animation ends.
            self.preview = [row[:] for row in self.game.board]
            self.start_animation_step(generation)
            return

    def start_animation_step(self, generation: int) -> None:
        if generation != self.ai_generation or self.ai_move is None or self.preview is None:
            return
        start = self.ai_move.start if self.ai_step == 0 else self.ai_move.path[self.ai_step - 1]
        end = self.ai_move.path[self.ai_step]
        piece = self.preview[start[0]][start[1]]
        assert piece is not None
        self.preview[start[0]][start[1]] = None
        self.animate_frame(generation, start, end, piece, 0)

    def animate_frame(
        self,
        generation: int,
        start: tuple[int, int],
        end: tuple[int, int],
        piece: str,
        frame: int,
    ) -> None:
        if generation != self.ai_generation or self.ai_move is None or self.preview is None:
            return
        if frame < ANIMATION_FRAMES:
            progress = frame / ANIMATION_FRAMES
            row = start[0] + (end[0] - start[0]) * progress
            col = start[1] + (end[1] - start[1]) * progress
            self.animated_piece = (piece, MARGIN + col * CELL, MARGIN + row * CELL)
            self.draw()
            self.root.after(
                ANIMATION_DELAY_MS,
                lambda: self.animate_frame(generation, start, end, piece, frame + 1),
            )
            return
        self.animated_piece = None
        self.preview[end[0]][end[1]] = piece
        if self.ai_move.captures:
            captured = self.ai_move.captures[self.ai_step]
            self.preview[captured[0]][captured[1]] = None
        self.ai_step += 1
        self.draw()
        if self.ai_step < len(self.ai_move.path):
            self.root.after(STEP_PAUSE_MS, lambda: self.start_animation_step(generation))
        else:
            self.root.after(STEP_PAUSE_MS, lambda: self.finish_computer_move(generation))

    def finish_computer_move(self, generation: int) -> None:
        if generation != self.ai_generation or self.ai_move is None:
            return
        move = self.ai_move
        self.game.play(move)
        self.moves.append(move)
        self.last_move = move
        self.ai_thinking = False
        self.clear_selection()
        self.persist()
        self.draw()

    def draw(self) -> None:
        self.renderer.draw()


def main() -> None:
    root = tk.Tk()
    DamaWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
