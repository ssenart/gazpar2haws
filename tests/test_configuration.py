"""Test the configuration module."""

import pytest
from pydantic import ValidationError

from gazpar2haws.configuration import Configuration
from gazpar2haws.model import Device


def test_configuration():

    config = Configuration.load("tests/config/configuration.yaml", "tests/config/secrets.yaml")

    assert config.logging.level == "debug"


@pytest.mark.parametrize("name", ["Compteur_de_gaz", "mon compteur", "gaz_été", "gaz-principal"])
def test_device_name_rejects_invalid_home_assistant_characters(name):

    with pytest.raises(ValidationError, match="Invalid name"):
        Device(name=name, data_source="test")


def test_device_name_accepts_lowercase_home_assistant_name():

    assert Device(name="gazpar_maison_1", data_source="test").name == "gazpar_maison_1"
