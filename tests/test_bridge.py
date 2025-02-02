"""Test the bridge module."""

import pytest

from gazpar2haws.bridge import Bridge
from gazpar2haws.configuration import Configuration


# ----------------------------------
# @pytest.mark.skip(reason="Requires Home Assistant server")
@pytest.mark.asyncio
async def test_run():

    # Load configuration
    config = Configuration.load(
        "tests/config/configuration.yaml", "tests/config/secrets.yaml"
    )  # pylint: disable=W0201

    bridge = Bridge(config)
    await bridge.run()
