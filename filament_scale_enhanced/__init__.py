# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin

from .fse_version import VERSION as __version__  # noqa: F401
from .hx711 import HX711

try:
    from RPi import GPIO
except (ModuleNotFoundError, RuntimeError):
    from Mock import GPIO  # noqa: F401


# pylint: disable=too-many-ancestors
class FilamentScalePlugin(
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.StartupPlugin,
):

    hx = None
    t = None
    tq = None

    @staticmethod
    def get_template_configs():  # pylint: disable=arguments-differ
        return [{"type": "settings", "custom_bindings": True}]

    @staticmethod
    def get_settings_defaults():  # pylint: disable=arguments-differ
        return {
            "tare": 8430152,
            "reference_unit": -411,
            "spool_weight": 200,
            "clockpin": 21,
            "datapin": 20,
            "lastknownweight": 0,
        }

    @staticmethod
    def get_assets():  # pylint: disable=arguments-differ
        return {
            "js": ["js/filament_scale.js"],
            "css": ["css/filament_scale.css"],
            "less": ["less/filament_scale.less"],
        }

    def __init__(self):
        super().__init__()
        self.mqtt_publish = lambda *args, **kwargs: None
        self.mqtt = False
        self.mqtt_topic = ''
        self.last_weight = 0
        self.last_sent_weight = -1

    def on_startup(self, host, port):  # pylint: disable=unused-argument
        try:
            self.hx = HX711(20, 21)
            self.hx.set_reading_format("LSB", "MSB")
            self.hx.reset()
            self.hx.power_up()
            self.t = octoprint.util.RepeatedTimer(3.0, self.check_weight)
            self.t.start()
            self.tq = octoprint.util.RepeatedTimer(10.0, self.send_weight_mqtt)
            self.tq.start()
        except Exception as err:  # pylint: disable=broad-exception-caught
            self._logger.exception(err)

    def on_after_startup(self):
        helpers = self._plugin_manager.get_helpers("mqtt", "mqtt_publish")
        if not helpers or "mqtt_publish" not in helpers:
            self._logger.debug(
                "MQTT plugin helpers not found scale value will not be published"
            )
            return

        base_topic = self._settings.global_get(
            ["plugins", "mqtt", "publish", "baseTopic"]
        )
        self.mqtt_topic = f"{base_topic.rstrip('/')}/plugin/{self._identifier}"
        self._logger.debug("Topic: %s", self.mqtt_topic)

        self.mqtt_publish = helpers["mqtt_publish"]
        self.mqtt = True
        self._logger.debug(
            "MQTT plugIn Helpers Found. Scale value will be published"
        )

    def real_weight(self) -> int:
        tare = self._settings.get(["tare"])
        reference = self._settings.get(["reference_unit"])
        spool = self._settings.get(["spool_weight"])
        weight = (self.last_weight - tare) / reference
        return int(weight) - int(spool)

    def send_weight_mqtt(self):
        if not self.mqtt:
            return
        real_weight = self.real_weight()
        if real_weight == self.last_sent_weight:
            return
        self.last_sent_weight = real_weight
        self.mqtt_publish(f'{self.mqtt_topic}/filament_weight', str(real_weight))

    def check_weight(self):
        self._logger.debug("Begin hxRead")
        try:
            self.hx.power_up()
            v = self.hx.read()
            self.last_weight = v
            self._plugin_manager.send_plugin_message(self._identifier, v)
            self.hx.power_down()
        except Exception as err:  # pylint: disable=broad-exception-caught
            self._logger.exception(err)

    # pylint: disable=line-too-long,use-dict-literal
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
                user="techman83",
                repo="Filament-Scale-Enhanced",
                current=self._plugin_version,
                # update method: pip
                pip="https://github.com/techman83/Filament-Scale-Enhanced/releases/latest/download/Filament_Scale_Enhanced.zip",  # noqa: E501
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
