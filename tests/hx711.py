import unittest

from octoprint_filament_scale.hx711 import HX711


class TestHx711(unittest.TestCase):

    def test_bool_list(self):
        bool_list = [False, False, False, False]
        self.assertListEqual(
            HX711.createBoolList(4),
            bool_list
        )
