"""Test the main module."""
import pytest
from gazpar2haws import __main__
import sys


# ----------------------------------
@pytest.mark.skip(reason="Requires Home Assistant server")
@pytest.mark.asyncio
async def test_main():

    # Simulate command line arguments
    sys.argv = ["gazpar2haws", "-c", "config/configuration.yaml", "-s", "config/secrets.yaml"]

    await __main__.main()
