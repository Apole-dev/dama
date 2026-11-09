import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dama import Game
from save import load_game, save_game


class SaveTests(unittest.TestCase):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch("save.SAVE_PATH", Path(directory) / "game.json"):
                game = Game()
                move = game.legal_moves()[0]
                game.play(move)
                save_game([move], "computer", "hard", "slate")
                loaded = load_game()
                self.assertIsNotNone(loaded)
                restored, moves, mode, difficulty, theme = loaded
                self.assertEqual(restored.board, game.board)
                self.assertEqual(restored.turn, game.turn)
                self.assertEqual(moves, [move])
                self.assertEqual((mode, difficulty, theme), ("computer", "hard", "slate"))

    def test_invalid_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "game.json"
            path.write_text("{}", encoding="utf-8")
            with patch("save.SAVE_PATH", path):
                self.assertIsNone(load_game())


if __name__ == "__main__":
    unittest.main()
