"""Regression test: the Home Assistant token must never reach the logs, even at DEBUG level (issue #124)."""

import json
import logging

import pytest
from websockets.asyncio.server import serve

from gazpar2haws.haws import HomeAssistantWS

TOKEN = "eyJhbGciOiJIUzI1NiJ9.TEST_TOKEN_PAYLOAD_abcdefghijklmnopqrstuvwxyz0123456789.TEST_TOKEN_SIGNATURE"


# ----------------------------------
async def _handler(websocket):
    await websocket.send(json.dumps({"type": "auth_required"}))
    await websocket.recv()
    await websocket.send(json.dumps({"type": "auth_ok"}))
    await websocket.wait_closed()


# ----------------------------------
class TestHomeAssistantWSLogging:
    # ----------------------------------
    @pytest.mark.asyncio
    async def test_token_is_not_logged_at_debug_level(self, caplog):

        caplog.set_level(logging.DEBUG)

        # The in-process test server logs the headers it receives: keep its logger quiet so that only the client is checked
        server_logger = logging.getLogger("tests.haws_logging.server")
        server_logger.setLevel(logging.INFO)

        async with serve(_handler, "127.0.0.1", 0, logger=server_logger) as server:
            port = server.sockets[0].getsockname()[1]

            haws = HomeAssistantWS("127.0.0.1", port, "/api/websocket", TOKEN)
            await haws.connect()
            await haws.disconnect()

        assert caplog.records, "Expected some log records to be captured"
        for record in caplog.records:
            assert TOKEN not in record.getMessage(), f"Token leaked in log record from {record.name}"
