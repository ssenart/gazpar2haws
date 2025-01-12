"""Test the bridge module."""

import pytest

from gazpar2haws import config_utils
from gazpar2haws.bridge import Bridge


# ----------------------------------
# @pytest.mark.skip(reason="Requires Home Assistant server")
@pytest.mark.asyncio
async def test_run():

    # Load configuration
    config = config_utils.ConfigLoader(
        "config/configuration.yaml", "config/secrets.yaml"
    )
    config.load_secrets()
    config.load_config()

    bridge = Bridge(config)
    await bridge.run()
