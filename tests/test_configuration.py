"""Test the configuration module."""

import pytest
from pydantic import ValidationError

from gazpar2haws.configuration import Configuration
from gazpar2haws.model import Device, Grdf


def test_configuration():

    config = Configuration.load("tests/config/configuration.yaml", "tests/config/secrets.yaml")

    assert config.logging.level == "debug"


def test_on_error_defaults_to_continue_so_existing_configurations_are_unaffected():

    config = Configuration.load("tests/config/configuration.yaml", "tests/config/secrets.yaml")

    assert config.grdf.on_error == "continue"


def test_on_error_accepts_stop():

    grdf = Grdf(on_error="stop", devices=[Device(name="gazpar2haws_test", data_source="test")])

    assert grdf.on_error == "stop"


def test_on_error_rejects_anything_else():

    with pytest.raises(ValidationError, match="on_error"):
        Grdf(on_error="retry", devices=[Device(name="gazpar2haws_test", data_source="test")])


@pytest.mark.parametrize("name", ["Compteur_de_gaz", "mon compteur", "gaz_été", "gaz-principal"])
def test_device_name_rejects_invalid_home_assistant_characters(name):

    with pytest.raises(ValidationError, match="Invalid name"):
        Device(name=name, data_source="test")


def test_device_name_accepts_lowercase_home_assistant_name():

    assert Device(name="gazpar_maison_1", data_source="test").name == "gazpar_maison_1"
