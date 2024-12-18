import websockets
import json
from datetime import datetime
import logging


# ----------------------------------
class HomeAssistantWS:
    def __init__(self, host, port, token):
        self._host = host
        self._port = port
        self._token = token
        self._websocket = None
        self._message_id = 1

    # ----------------------------------
    async def connect(self):

        logging.debug(f"Connecting to Home Assistant at {self._host}:{self._port}")

        ws_url = f"ws://{self._host}:{self._port}/api/websocket"

        # Connect to the websocket
        self._websocket = await websockets.connect(ws_url)

        # When a client connects to the server, the server sends out auth_required.
        connect_response = await self._websocket.recv()
        connect_response_data = json.loads(connect_response)

        if connect_response_data.get("type") != "auth_required":
            message = f"Authentication failed: auth_required not received {connect_response_data.get('messsage')}"
            logging.warning(message)
            raise Exception(message)

        # The first message from the client should be an auth message. You can authorize with an access token.
        auth_message = {"type": "auth", "access_token": self._token}
        await self._websocket.send(json.dumps(auth_message))

        # If the client supplies valid authentication, the authentication phase will complete by the server sending the auth_ok message.
        auth_response = await self._websocket.recv()
        auth_response_data = json.loads(auth_response)

        if auth_response_data.get("type") == "auth_invalid":
            message = f"Authentication failed: {auth_response_data.get('messsage')}"
            logging.warning(message)
            raise Exception(message)

        logging.debug("Connected to Home Assistant")

    # ----------------------------------
    async def disconnect(self):

        logging.debug("Disconnecting from Home Assistant...")

        await self._websocket.close()

        logging.debug("Disconnected from Home Assistant")

    # ----------------------------------
    async def send_message(self, message: dict) -> dict:

        logging.debug("Sending a message...")

        message["id"] = self._message_id

        self._message_id += 1

        await self._websocket.send(json.dumps(message))

        response = await self._websocket.recv()

        response_data = json.loads(response)

        logging.debug(f"Received response: {response_data}")

        if response_data.get("type") != "result":
            raise Exception(f"Invalid response message: {response_data}")

        if not response_data.get("success"):
            raise Exception(f"Request failed: {response_data.get('error')}")

        return response_data.get("result")

    # ----------------------------------
    async def statistics_during_period(self, entity_ids: list[str], start_time: datetime, end_time: datetime) -> dict:

        logging.debug(f"Getting {entity_ids} statistics during period from {start_time} to {end_time}...")

        # Subscribe to statistics
        statistics_message = {
            "type": "recorder/statistics_during_period",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "statistic_ids": entity_ids,
            "period": "day"
        }

        response = await self.send_message(statistics_message)

        logging.debug(f"Received {entity_ids} statistics during period from {start_time} to {end_time}")

        return response

    # ----------------------------------
    async def get_last_statistic(self, entity_id: str) -> dict:

        logging.debug(f"Getting last statistic for {entity_id}...")

        statistics = await self.statistics_during_period([entity_id], datetime.now() - datetime.timedelta(days=30), datetime.now())

        logging.debug(f"Last statistic for {entity_id}: {statistics[entity_id][-1]}")

        return statistics[entity_id][-1]

    # ----------------------------------
    async def import_statistics(self, entity_id: str, source: str, name: str, statistics: list[dict]):

        logging.debug(f"Importing {len(statistics)} statistics for {entity_id} from {source}...")

        # Import statistics message
        import_statistics_message = {
            "type": "recorder/import_statistics",
            "metadata": {
                    "has_mean": False,
                    "has_sum": True,
                    "statistic_id": entity_id,
                    "source": source,
                    "name": name,
                    "unit_of_measurement": 'kWh',
            },
            "stats": statistics
        }

        await self.send_message(import_statistics_message)

        logging.debug(f"Imported {len(statistics)} statistics for {entity_id} from {source}")

    # ----------------------------------
    async def clear_statistics(self, entity_ids: list[str]):

        logging.debug(f"Clearing {entity_ids} statistics...")

        # Clear statistics message
        clear_statistics_message = {
            "type": "recorder/clear_statistics",
            "statistic_ids": entity_ids
        }

        await self.send_message(clear_statistics_message)

        logging.debug(f"Cleared {entity_ids} statistics")
