import unittest

from src import player, web
from src.labels import format_score


class ScoreTests(unittest.TestCase):
    def test_shared_label(self):
        self.assertEqual(format_score(2, 1), "2 - 1")

    def test_web_label(self):
        self.assertEqual(web.render_score(0, 0), "0 - 0")

    def test_player_label(self):
        self.assertEqual(player.render_score(2, 1), "2 - 1")


if __name__ == "__main__":
    unittest.main()
