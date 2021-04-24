import unittest

from filament_scale_enhanced.hx711 import HX711


class TestHx711(unittest.TestCase):

    def test_bool_list(self):
        bool_list = [False, False, False, False]
        self.assertListEqual(
            HX711.createBoolList(4),
            bool_list
        )
