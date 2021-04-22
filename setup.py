# mypy: ignore_errors=True
# pylint: disable=invalid-name

from setuptools import setup

try:
    import octoprint_setuptools
except ModuleNotFoundError:
    print(
        "Could not import OctoPrint's setuptools, are you sure you are "
        "running that under the same python installation that OctoPrint "
        "is installed under?"
    )
    import sys
    sys.exit(-1)

plugin_identifier = "filament_scale_enhanced"
plugin_package = "filament_scale_enhanced"
plugin_name = "Filament Scale Enhanced"
plugin_version = "0.2.0"
plugin_description = ("Plugin for integrating a load cell into a filament "
                      "holder.")
plugin_author = "Victor Noordhoek / Leon Wright"
plugin_author_email = "techman83@gmail.com"
plugin_url = "https://github.com/dieki-n/OctoPrint-Filament-Scale"
plugin_license = "AGPLv3"
plugin_requires = ["RPi.GPIO"]
plugin_extras_require = {
    'development': [
        'autopep8',
        'pytest',
        'pytest-mypy',
        'mypy',
        'pytest-pylint',
        'pylint',
        'pytest-flake8',
    ],
    'test': [
        'pytest',
        'pytest-mypy',
        'mypy',
        'pytest-pylint',
        'pylint',
        'pytest-flake8',
    ]
}

plugin_additional_data = []
plugin_additional_packages = []
plugin_ignored_packages = []
additional_setup_parameters = {}

setup_parameters = octoprint_setuptools.create_plugin_setup_parameters(
    identifier=plugin_identifier,
    package=plugin_package,
    name=plugin_name,
    version=plugin_version,
    description=plugin_description,
    author=plugin_author,
    mail=plugin_author_email,
    url=plugin_url,
    license=plugin_license,
    requires=plugin_requires,
    additional_packages=plugin_additional_packages,
    ignored_packages=plugin_ignored_packages,
    additional_data=plugin_additional_data,
    extra_requires=plugin_extras_require
)

if len(additional_setup_parameters):
    from octoprint.util import dict_merge
    setup_parameters = dict_merge(setup_parameters,
                                  additional_setup_parameters)

setup(**setup_parameters)
