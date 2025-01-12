"""Test the main module."""

import sys

import pytest

from gazpar2haws import __main__


# ----------------------------------
# @pytest.mark.skip(reason="Requires Home Assistant server")
@pytest.mark.asyncio
async def test_main():

    # Simulate command line arguments
    sys.argv = [
        "gazpar2haws",
        "-c",
        "tests/config/configuration.yaml",
        "-s",
        "tests/config/secrets.yaml",
    ]

    await __main__.main()
