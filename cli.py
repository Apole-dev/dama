from dama import Game, Move, Position


def print_board(game: Game) -> None:
    print("  a b c d e f g h")
    for row, cells in enumerate(game.board):
        print(f"{8 - row} " + " ".join(piece or "." for piece in cells))
    print("r red, w white, uppercase king")


def format_move(move: Move) -> str:
    def square(position: Position) -> str:
        return f"{chr(ord('a') + position[1])}{8 - position[0]}"

    separator = "x" if move.captures else "-"
    return separator.join(square(position) for position in (move.start,) + move.path)


def main() -> None:
    game = Game()
    while not game.finished:
        print_board(game)
        moves = game.legal_moves()
        print(f"{game.turn} to move")
        for number, move in enumerate(moves, 1):
            print(f"{number}. {format_move(move)}")
        choice = input("Move number or q: ").strip().lower()
        if choice == "q":
            return
        if not choice.isdigit() or not 1 <= int(choice) <= len(moves):
            print("Invalid choice")
            continue
        game.play(moves[int(choice) - 1])
    print_board(game)
    print("Draw" if game.draw_reason else f"{game.winner} wins")


if __name__ == "__main__":
    main()
