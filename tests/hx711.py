import unittest

from filament_scale_enhanced.hx711 import HX711
from filament_scale_enhanced import FilamentScalePlugin


class TestHx711(unittest.TestCase):

    def test_bool_list(self):
        bool_list = [False, False, False, False]
        self.assertListEqual(
            HX711.createBoolList(4),
            bool_list
        )


class TestFilamentScalePlugin(unittest.TestCase):

    def test_settings_dict_defaults(self):
        defaults = {
            'tare': 8430152,
            'reference_unit': -411,
            'spool_weight': 200,
            'clockpin': 21,
            'datapin': 20,
            'lastknownweight': 0
        }
        self.assertDictEqual(FilamentScalePlugin.get_settings_defaults(), defaults)
