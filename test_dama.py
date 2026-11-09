import unittest

from dama import Game, Move, RED, WHITE


def empty_board():
    return [[None for _ in range(8)] for _ in range(8)]


class GameTests(unittest.TestCase):
    def test_initial_position(self):
        game = Game()
        self.assertEqual(sum(cell == "r" for row in game.board for cell in row), 12)
        self.assertEqual(sum(cell == "w" for row in game.board for cell in row), 12)
        self.assertEqual(game.turn, RED)
        self.assertEqual(len(game.legal_moves()), 7)

    def test_capture_is_required_and_chain_continues(self):
        board = empty_board()
        board[5][2] = "r"
        board[4][3] = "w"
        board[2][5] = "w"
        board[5][6] = "r"
        game = Game(board)
        move = Move((5, 2), ((3, 4), (1, 6)), ((4, 3), (2, 5)))
        self.assertEqual(game.legal_moves(), [move])
        game.play(move)
        self.assertEqual(game.board[1][6], "r")
        self.assertIsNone(game.board[4][3])
        self.assertIsNone(game.board[2][5])

    def test_crowning_ends_capture(self):
        board = empty_board()
        board[2][1] = "r"
        board[1][2] = "w"
        board[1][4] = "w"
        game = Game(board)
        move = Move((2, 1), ((0, 3),), ((1, 2),))
        self.assertEqual(game.legal_moves(), [move])
        game.play(move)
        self.assertEqual(game.board[0][3], "R")

    def test_king_can_move_and_capture_backward(self):
        board = empty_board()
        board[3][2] = "R"
        board[4][3] = "w"
        game = Game(board)
        self.assertEqual(game.legal_moves(), [Move((3, 2), ((5, 4),), ((4, 3),))])

    def test_player_with_no_move_loses(self):
        board = empty_board()
        board[7][0] = "w"
        board[1][2] = "r"
        game = Game(board, WHITE)
        self.assertEqual(game.winner, RED)

    def test_undo_restores_board_and_turn(self):
        game = Game()
        before = [row[:] for row in game.board]
        game.play(game.legal_moves()[0])
        self.assertEqual(game.turn, WHITE)
        self.assertTrue(game.undo())
        self.assertEqual(game.board, before)
        self.assertEqual(game.turn, RED)
        self.assertFalse(game.undo())


if __name__ == "__main__":
    unittest.main()
