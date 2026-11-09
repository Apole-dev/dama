import tkinter as tk
from typing import Protocol

from dama import Game, Move, Position, RED, SIZE


CELL = 68
MARGIN = 14
BOARD_SIZE = CELL * SIZE
PANEL_WIDTH = 212
LIGHT = "#edcf9c"
DARK = "#855336"
FRAME = "#4b2e21"
BACKGROUND = "#241b18"
ACCENT = "#e7bc67"


class RenderState(Protocol):
    screen: str
    difficulty: str
    theme: str
    saved_game: object | None
    moves: list[Move]
    game: Game
    selected: Position | None
    candidates: list[Move]
    step_index: int
    preview: list[list[str | None]] | None
    last_move: Move | None
    ai_thinking: bool
    ai_error: bool
    ai_move: Move | None
    ai_step: int
    animated_piece: tuple[str, float, float] | None


class GameRenderer:
    def __init__(self, canvas: tk.Canvas, state: RenderState):
        self.canvas = canvas
        self.state = state

    def draw(self) -> None:
        self.canvas.delete("all")
        if self.state.screen == "menu":
            self.draw_menu()
            return
        self.draw_board()
        self.draw_panel()
        if self.state.game.winner is not None:
            self.draw_result()

    def colors(self) -> tuple[str, str, str, str, str, str, str]:
        if self.state.theme == "slate":
            return "#cbd5df", "#506275", "#263747", "#bd5650", "#f1eee5", "#713638", "#858e95"
        return LIGHT, DARK, FRAME, "#c95749", "#e9dfcb", "#71332d", "#8e806b"

    def draw_menu(self) -> None:
        self.canvas.create_rectangle(0, 0, 784, 572, fill=BACKGROUND, outline="")
        self.canvas.create_text(
            52, 81, anchor="nw", text="DAMA", fill="#f4dfb9",
            font=("DejaVu Sans", 46, "bold")
        )
        self.canvas.create_line(52, 156, 200, 156, fill="#b95b47", width=3)
        self.draw_menu_card(52, 205, "İki oyuncu")
        self.draw_menu_card(52, 291, "Bilgisayara karşı")
        self.canvas.create_text(
            52, 398, anchor="nw", text="SEVİYE", fill="#a99983",
            font=("DejaVu Sans", 10, "bold")
        )
        labels = (("easy", "Kolay", 52), ("normal", "Orta", 186), ("hard", "Zor", 320))
        for value, label, x in labels:
            active = value == self.state.difficulty
            self.canvas.create_rectangle(
                x, 426, x + 122, 472,
                fill="#95553e" if active else "#302620",
                outline="#be8160" if active else "#665044", width=2
            )
            self.canvas.create_text(
                x + 61, 449, text=label,
                fill="#fff0d2" if active else "#a99983",
                font=("DejaVu Sans", 12, "bold")
            )
        self.draw_menu_art()
        if self.state.saved_game is not None:
            self.draw_menu_option(503, 410, "Devam et")
        self.draw_menu_option(503, 474, "Tema  " + ("Klasik" if self.state.theme == "classic" else "Arduvaz"))

    def draw_menu_option(self, x: int, y: int, label: str) -> None:
        self.canvas.create_rectangle(x, y, x + 232, y + 44, fill="#342722", outline="#8e684d", width=2)
        self.canvas.create_text(x + 116, y + 22, text=label, fill="#f6dfba", font=("DejaVu Sans", 12, "bold"))

    def draw_menu_art(self) -> None:
        light, dark, _, red_face, white_face, red_rim, white_rim = self.colors()
        for row in range(4):
            for col in range(4):
                x = 503 + col * 58
                y = 155 + row * 58
                self.canvas.create_rectangle(
                    x, y, x + 58, y + 58,
                    fill=dark if (row + col) % 2 else light,
                    outline="#694734", width=1
                )
        for row, col, fill, outline in (
            (0, 1, white_face, white_rim),
            (0, 3, white_face, white_rim),
            (3, 0, red_face, red_rim),
            (3, 2, red_face, red_rim),
        ):
            x = 503 + col * 58 + 29
            y = 155 + row * 58 + 29
            self.canvas.create_oval(
                x - 22, y - 20, x + 22, y + 24,
                fill="#2d211d", outline=""
            )
            self.canvas.create_oval(
                x - 22, y - 23, x + 22, y + 21,
                fill=fill, outline=outline, width=3
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
        light, dark, frame, _, _, _, _ = self.colors()
        x0 = MARGIN
        y0 = MARGIN
        self.canvas.create_rectangle(
            x0 - 7, y0 - 7, x0 + BOARD_SIZE + 7, y0 + BOARD_SIZE + 7,
            fill=frame, outline="#b88a56", width=3
        )
        board = self.state.preview if self.state.preview is not None else self.state.game.board
        destinations = (
            {move.path[self.state.step_index] for move in self.state.candidates}
            if self.state.candidates else set()
        )
        selectable = (
            {move.start for move in self.state.game.legal_moves()}
            if self.state.selected is None and not self.state.ai_thinking else set()
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
                    fill=dark if (row + col) % 2 else light,
                    outline="#71482f", width=1
                )
                if self.state.last_move and square in (self.state.last_move.start, self.state.last_move.end):
                    self.canvas.create_rectangle(
                        x1 + 4, y1 + 4, x2 - 4, y2 - 4,
                        outline="#ebc86e", width=3
                    )
                if square == self.state.selected:
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
        if self.state.animated_piece is not None:
            piece, x, y = self.state.animated_piece
            self.draw_piece(x, y, piece, False)

    def draw_piece(self, x: float, y: float, piece: str, selectable: bool) -> None:
        _, _, _, red_face, white_face, red_rim, white_rim = self.colors()
        red = piece.lower() == "r"
        rim = red_rim if red else white_rim
        face = red_face if red else white_face
        ring = "#a8453b" if red else "#b6a88e"
        self.canvas.create_oval(
            x + 11, y + 15, x + CELL - 9, y + CELL - 6,
            fill="#38251f", outline=""
        )
        self.canvas.create_oval(
            x + 9, y + 9, x + CELL - 9, y + CELL - 11,
            fill=rim, outline="#51342a", width=2
        )
        self.canvas.create_oval(
            x + 13, y + 12, x + CELL - 13, y + CELL - 15,
            fill=face, outline="#e78d7b" if red else "#fff8e9", width=2
        )
        self.canvas.create_oval(
            x + 21, y + 20, x + CELL - 21, y + CELL - 23,
            outline=ring, width=2
        )
        if piece.isupper():
            self.canvas.create_text(
                x + CELL // 2, y + CELL // 2 - 1,
                text="♛", fill="#f7dfaa" if red else "#7d6445",
                font=("DejaVu Sans", 23, "bold")
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
        if self.state.game.winner:
            status = "Kırmızı kazandı" if self.state.game.winner == RED else "Beyaz kazandı"
        elif self.state.ai_error:
            status = "Motor açılamadı"
        elif self.state.ai_thinking:
            if self.state.ai_move and self.state.ai_move.captures:
                step = min(self.state.ai_step + 1, len(self.state.ai_move.path))
                status = f"Rakip alıyor {step}/{len(self.state.ai_move.path)}"
            else:
                status = "Rakip oynuyor" if self.state.ai_move else "Rakip düşünüyor"
        elif self.state.preview is not None:
            status = "Almaya devam et"
        else:
            status = "Kırmızı oynuyor" if self.state.game.turn == RED else "Beyaz oynuyor"
        self.canvas.create_text(
            x, 117, anchor="nw", text=status, fill=ACCENT,
            font=("DejaVu Sans", 14, "bold")
        )
        board = self.state.preview if self.state.preview is not None else self.state.game.board
        red_count = sum(piece is not None and piece.lower() == "r"
                        for row in board for piece in row)
        white_count = sum(piece is not None and piece.lower() == "w"
                          for row in board for piece in row)
        if self.state.animated_piece is not None:
            if self.state.animated_piece[0].lower() == "r":
                red_count += 1
            else:
                white_count += 1
        self.canvas.create_text(
            x, 183, anchor="nw", text=f"Kırmızı  {red_count}",
            fill="#e8c5b8", font=("DejaVu Sans", 13)
        )
        self.canvas.create_text(
            x, 213, anchor="nw", text=f"Beyaz    {white_count}",
            fill="#f0e7d5", font=("DejaVu Sans", 13)
        )
        self.draw_button(x, 300, "Yeni oyun", True)
        self.draw_button(x, 354, "Geri al", self.state.preview is not None or bool(self.state.game.history))
        self.draw_button(x, 408, "Menü", True)
        self.canvas.create_text(x, 465, anchor="nw", text="HAMLELER", fill="#a99983", font=("DejaVu Sans", 10, "bold"))
        self.canvas.create_text(x + 170, 465, anchor="ne", text="Tümü", fill=ACCENT, font=("DejaVu Sans", 10))
        for index, move in enumerate(self.state.moves[-3:], start=max(0, len(self.state.moves) - 3)):
            start = f"{chr(97 + move.start[1])}{8 - move.start[0]}"
            end = f"{chr(97 + move.end[1])}{8 - move.end[0]}"
            action = "x" if move.captures else "-"
            label = f"{index + 1}. {start}{action}{end}"
            if len(move.captures) > 1:
                label += f"  {len(move.captures)} taş"
            self.canvas.create_text(x, 486 + (index - max(0, len(self.state.moves) - 3)) * 24,
                                    anchor="nw", text=label, fill="#e8c5b8", font=("DejaVu Sans", 11))

    def draw_result(self) -> None:
        self.canvas.create_rectangle(118, 174, 450, 422, fill="#241b18", outline="#d7ad76", width=3)
        winner = "Kırmızı kazandı" if self.state.game.winner == RED else "Beyaz kazandı"
        self.canvas.create_text(284, 227, text="OYUN BİTTİ", fill="#a99983", font=("DejaVu Sans", 12, "bold"))
        self.canvas.create_text(284, 268, text=winner, fill=ACCENT, font=("DejaVu Sans", 20, "bold"))
        self.draw_button(198, 307, "Yeniden oyna", True)
        self.draw_button(198, 361, "Menü", True)

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
