# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin

from .hx711 import HX711

try:
    import RPi.GPIO as GPIO
except (ModuleNotFoundError, RuntimeError):
    import Mock.GPIO as GPIO  # noqa: F401


# pylint: disable=too-many-ancestors
class FilamentScalePlugin(octoprint.plugin.SettingsPlugin,
                          octoprint.plugin.AssetPlugin,
                          octoprint.plugin.TemplatePlugin,
                          octoprint.plugin.StartupPlugin):

    hx = None
    t = None

    @staticmethod
    def get_template_configs():
        return [
            dict(type="settings", custom_bindings=True)
        ]

    @staticmethod
    def get_settings_defaults():
        return dict(
            tare=8430152,
            refernce_unit=-411,
            spool_weight=200,
            clockpin=21,
            datapin=20,
            lastknownweight=0
        )

    @staticmethod
    def get_assets():
        return dict(
            js=["js/filament_scale.js"],
            css=["css/filament_scale.css"],
            less=["less/filament_scale.less"]
        )

    def on_startup(self, host, port):  # pylint: disable=unused-argument
        self.hx = HX711(20, 21)
        self.hx.set_reading_format("LSB", "MSB")
        self.hx.reset()
        self.hx.power_up()
        self.t = octoprint.util.RepeatedTimer(3.0, self.check_weight)
        self.t.start()

    def check_weight(self):
        self.hx.power_up()
        v = self.hx.read()
        self._plugin_manager.send_plugin_message(self._identifier, v)
        self.hx.power_down()

    def get_update_information(self):
        # Define the configuration for your plugin to use with the
        # Software Update Plugin here.
        # See https://github.com/foosel/OctoPrint/wiki/Plugin:-Software-Update
        # for details.
        return dict(
            filament_scale=dict(
                displayName="Filament Scale Plugin",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="dieki-n",
                repo="OctoPrint-Filament-scale",
                current=self._plugin_version,

                # update method: pip
                pip="https://github.com/dieki-n/OctoPrint-Filament-scale/archive/{target_version}.zip"
            )
        )


__plugin_name__ = "Filament Scale"  # pylint: disable=global-variable-undefined
__plugin_pythoncompat__ = ">=3,<4"  # pylint: disable=global-variable-undefined


# pylint: disable=global-variable-undefined
def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = FilamentScalePlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin5.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
