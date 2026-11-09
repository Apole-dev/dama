import unittest

from computer import choose_move
from dama import Game, WHITE


class ComputerTests(unittest.TestCase):
    def test_computer_chooses_legal_move(self):
        game = Game()
        game.play(game.legal_moves()[0])
        for difficulty in ("easy", "normal", "hard"):
            self.assertIn(choose_move(game, difficulty), game.legal_moves())

    def test_computer_takes_forced_capture(self):
        board = [[None for _ in range(8)] for _ in range(8)]
        board[2][3] = "w"
        board[3][4] = "r"
        game = Game(board, WHITE)
        move = choose_move(game, "normal")
        self.assertEqual(move.captures, ((3, 4),))

    def test_computer_maps_capture_chain(self):
        board = [[None for _ in range(8)] for _ in range(8)]
        board[2][3] = "w"
        board[3][4] = "r"
        board[5][6] = "r"
        game = Game(board, WHITE)
        move = choose_move(game, "normal")
        self.assertEqual(move.path, ((4, 5), (6, 7)))
        self.assertEqual(move.captures, ((3, 4), (5, 6)))


if __name__ == "__main__":
    unittest.main()
