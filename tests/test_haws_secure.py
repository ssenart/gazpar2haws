"""Unit tests for HomeAssistantWS TLS (wss://) support."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from gazpar2haws.haws import HomeAssistantWS


def _make_recv_side_effect():
    return [
        json.dumps({"type": "auth_required"}),
        json.dumps({"type": "auth_ok"}),
    ]


# ----------------------------------
class TestHomeAssistantWSSecure:

    # ----------------------------------
    @pytest.mark.asyncio
    async def test_connect_uses_ws_scheme_by_default(self):

        haws = HomeAssistantWS("myhost", 8123, "/api/websocket", "token")

        mock_websocket = AsyncMock()
        mock_websocket.recv.side_effect = _make_recv_side_effect()

        with patch("gazpar2haws.haws.websockets.connect", new=AsyncMock(return_value=mock_websocket)) as mock_connect:
            await haws.connect()

        args, kwargs = mock_connect.call_args
        assert args[0] == "ws://myhost:8123/api/websocket"
        assert kwargs["ssl"] is None

    # ----------------------------------
    @pytest.mark.asyncio
    async def test_connect_uses_wss_scheme_when_secure(self):

        haws = HomeAssistantWS("myhost", 8123, "/api/websocket", "token", secure=True)

        mock_websocket = AsyncMock()
        mock_websocket.recv.side_effect = _make_recv_side_effect()

        with patch("gazpar2haws.haws.websockets.connect", new=AsyncMock(return_value=mock_websocket)) as mock_connect:
            await haws.connect()

        args, kwargs = mock_connect.call_args
        assert args[0] == "wss://myhost:8123/api/websocket"
        assert kwargs["ssl"] is not None
        assert kwargs["ssl"].verify_mode.name == "CERT_REQUIRED"

    # ----------------------------------
    @pytest.mark.asyncio
    async def test_connect_disables_verification_when_verify_ssl_false(self):

        haws = HomeAssistantWS("myhost", 8123, "/api/websocket", "token", secure=True, verify_ssl=False)

        mock_websocket = AsyncMock()
        mock_websocket.recv.side_effect = _make_recv_side_effect()

        with patch("gazpar2haws.haws.websockets.connect", new=AsyncMock(return_value=mock_websocket)) as mock_connect:
            await haws.connect()

        args, kwargs = mock_connect.call_args
        assert args[0] == "wss://myhost:8123/api/websocket"
        assert kwargs["ssl"].check_hostname is False
        assert kwargs["ssl"].verify_mode.name == "CERT_NONE"
