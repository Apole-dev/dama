import unittest

from dama import Game, Move, RED, WHITE
from record import export_pdn, move_text


class RecordTests(unittest.TestCase):
    def test_pdn_uses_board_coordinates_and_result(self):
        game = Game()
        first = Move((5, 0), ((4, 1),))
        game.play(first)
        second = game.legal_moves()[0]
        game.play(second)
        record = export_pdn(game, [first, second])
        self.assertIn('[GameType "21,B,8,8,A0,0"]', record)
        self.assertIn("1. a3-b4", record)
        self.assertIn(move_text(second), record)
        self.assertTrue(record.endswith("*\n"))

    def test_capture_path(self):
        move = Move((5, 2), ((3, 4), (1, 6)), ((4, 3), (2, 5)))
        self.assertEqual(move_text(move), "c3xe5xg7")

    def test_result_uses_white_black_order(self):
        game = Game()
        game.winner = RED
        self.assertIn('[Result "0-1"]', export_pdn(game, []))
        game.winner = WHITE
        self.assertIn('[Result "1-0"]', export_pdn(game, []))


if __name__ == "__main__":
    unittest.main()
