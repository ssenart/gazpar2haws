"""Test the configuration module."""

from gazpar2haws.configuration import Configuration


def test_configuration():

    config = Configuration.load("tests/config/configuration.yaml", "tests/config/secrets.yaml")

    assert config.logging.level == "debug"
