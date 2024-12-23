import websockets
import json
from datetime import datetime, timedelta
import logging

Logger = logging.getLogger(__name__)


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

        Logger.debug(f"Connecting to Home Assistant at {self._host}:{self._port}")

        ws_url = f"ws://{self._host}:{self._port}/api/websocket"

        # Connect to the websocket
        self._websocket = await websockets.connect(ws_url)

        # When a client connects to the server, the server sends out auth_required.
        connect_response = await self._websocket.recv()
        connect_response_data = json.loads(connect_response)

        if connect_response_data.get("type") != "auth_required":
            message = f"Authentication failed: auth_required not received {connect_response_data.get('messsage')}"
            Logger.warning(message)
            raise Exception(message)

        # The first message from the client should be an auth message. You can authorize with an access token.
        auth_message = {"type": "auth", "access_token": self._token}
        await self._websocket.send(json.dumps(auth_message))

        # If the client supplies valid authentication, the authentication phase will complete by the server sending the auth_ok message.
        auth_response = await self._websocket.recv()
        auth_response_data = json.loads(auth_response)

        if auth_response_data.get("type") == "auth_invalid":
            message = f"Authentication failed: {auth_response_data.get('messsage')}"
            Logger.warning(message)
            raise Exception(message)

        Logger.debug("Connected to Home Assistant")

    # ----------------------------------
    async def disconnect(self):

        Logger.debug("Disconnecting from Home Assistant...")

        await self._websocket.close()

        Logger.debug("Disconnected from Home Assistant")

    # ----------------------------------
    async def send_message(self, message: dict) -> dict:

        Logger.debug("Sending a message...")

        message["id"] = self._message_id

        self._message_id += 1

        await self._websocket.send(json.dumps(message))

        response = await self._websocket.recv()

        response_data = json.loads(response)

        Logger.debug("Received response")

        if response_data.get("type") != "result":
            raise Exception(f"Invalid response message: {response_data}")

        if not response_data.get("success"):
            raise Exception(f"Request failed: {response_data.get('error')}")

        return response_data.get("result")

    # ----------------------------------
    async def list_statistic_ids(self, statistic_type: str = None) -> list[str]:

        Logger.debug("Listing statistics IDs...")

        # List statistics IDs message
        list_statistic_ids_message = {
            "type": "recorder/list_statistic_ids"
        }

        if statistic_type is not None:
            list_statistic_ids_message["statistic_type"] = statistic_type

        response = await self.send_message(list_statistic_ids_message)

        Logger.debug(f"Listed statistics IDs: {len(response)} ids")

        return response

    # ----------------------------------
    async def exists_statistic_id(self, entity_id: str, statistic_type: str = None) -> bool:

        Logger.debug(f"Checking if {entity_id} exists...")

        statistic_ids = await self.list_statistic_ids(statistic_type)

        entity_ids = [statistic_id.get("statistic_id") for statistic_id in statistic_ids]

        exists_statistic = entity_id in entity_ids

        Logger.debug(f"{entity_id} exists: {exists_statistic}")

        return exists_statistic

    # ----------------------------------
    async def statistics_during_period(self, entity_ids: list[str], start_time: datetime, end_time: datetime) -> dict:

        Logger.debug(f"Getting {entity_ids} statistics during period from {start_time} to {end_time}...")

        # Subscribe to statistics
        statistics_message = {
            "type": "recorder/statistics_during_period",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "statistic_ids": entity_ids,
            "period": "day"
        }

        response = await self.send_message(statistics_message)

        Logger.debug(f"Received {entity_ids} statistics during period from {start_time} to {end_time}")

        return response

    # ----------------------------------
    async def get_last_statistic(self, entity_id: str) -> dict:

        Logger.debug(f"Getting last statistic for {entity_id}...")

        statistics = await self.statistics_during_period([entity_id], datetime.now() - timedelta(days=30), datetime.now())

        Logger.debug(f"Last statistic for {entity_id}: {statistics[entity_id][-1]}")

        return statistics[entity_id][-1]

    # ----------------------------------
    async def import_statistics(self, entity_id: str, source: str, name: str, unit_of_measurement: str, statistics: list[dict]):

        Logger.debug(f"Importing {len(statistics)} statistics for {entity_id} from {source}...")

        if len(statistics) == 0:
            Logger.debug("No statistics to import")
            return

        # Import statistics message
        import_statistics_message = {
            "type": "recorder/import_statistics",
            "metadata": {
                    "has_mean": False,
                    "has_sum": True,
                    "statistic_id": entity_id,
                    "source": source,
                    "name": name,
                    "unit_of_measurement": unit_of_measurement,
            },
            "stats": statistics
        }

        await self.send_message(import_statistics_message)

        Logger.debug(f"Imported {len(statistics)} statistics for {entity_id} from {source}")

    # ----------------------------------
    async def clear_statistics(self, entity_ids: list[str]):

        Logger.debug(f"Clearing {entity_ids} statistics...")

        # Clear statistics message
        clear_statistics_message = {
            "type": "recorder/clear_statistics",
            "statistic_ids": entity_ids
        }

        await self.send_message(clear_statistics_message)

        Logger.debug(f"Cleared {entity_ids} statistics")
