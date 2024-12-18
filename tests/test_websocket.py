import asyncio
import websockets
import json
import datetime


# Replace with your Home Assistant URL and Long-Lived Access Token
HA_URL = "ws://192.168.1.223:8123/api/websocket"
HA_ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI4Y2RjOWM5YWFlM2E0OGY3OWMzN2FjMTYzMTc5NGNiOSIsImlhdCI6MTczNDMwMjIyMywiZXhwIjoyMDQ5NjYyMjIzfQ.OSCVw-Dy4r5iKrLNr5DLFp4_LWzR1kyEWZkjua5FVWQ"


async def get_last_statistic(entity_id):
    async with websockets.connect(HA_URL) as websocket:

        # When a client connects to the server, the server sends out auth_required.
        connect_response = await websocket.recv()
        connect_response_data = json.loads(connect_response)

        if connect_response_data.get("type") != "auth_required":
            raise Exception("Authentication failed: auth_required not received")

        # The first message from the client should be an auth message. You can authorize with an access token.
        auth_message = {"type": "auth", "access_token": HA_ACCESS_TOKEN}
        await websocket.send(json.dumps(auth_message))

        # If the client supplies valid authentication, the authentication phase will complete by the server sending the auth_ok message.
        auth_response = await websocket.recv()
        auth_response_data = json.loads(auth_response)

        if auth_response_data.get("type") == "auth_invalid":
            raise Exception(f"Authentication failed: {auth_response_data.get("messsage")}")

        # Subscribe to statistics
        request_id = 1
        subscribe_message = {
            "id": request_id,
            "type": "recorder/statistics_during_period",
            "start_time": (datetime.datetime.now() - datetime.timedelta(days=30)).isoformat(),  # 1 month ago
            "end_time": datetime.datetime.now().isoformat(),  # Use current time for recent data
            "statistic_ids": [entity_id],
            "period": "day"
        }

        await websocket.send(json.dumps(subscribe_message))

        # Wait for response
        response = await websocket.recv()
        response_data = json.loads(response)

        if "result" in response_data and response_data["result"]:
            statistics = response_data["result"]
            print(f"Last statistic for {entity_id}: {statistics[entity_id][-1]}")
            return statistics[entity_id][-1]  # Return the last statistic
        else:
            print(f"No statistics found for {entity_id}")
            return None


def test_websocket():

    # Replace 'sensor.your_sensor_id' with your actual entity ID
    entity_id = "sensor.gazpar"

    statistics = asyncio.run(get_last_statistic(entity_id))

    assert statistics is not None

    # Extract the date and convert into a datetime object
    date = datetime.datetime.fromtimestamp(int(statistics["start"]) / 1000)

    print(f"Last statistic for {entity_id} was recorded on {date}")
