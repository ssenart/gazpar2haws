import pygazpar
import traceback
import logging
import pytz
from typing import Any
from datetime import datetime
from gazpar2haws.haws import HomeAssistantWS


# ----------------------------------
class Gazpar:

    # ----------------------------------
    def __init__(self, config: dict[str, Any], homeassistant: HomeAssistantWS):
        self._config = config
        self._device_name = config.get("name")
        self._homeassistant = homeassistant

    # ----------------------------------
    def name(self):
        return self._device_name

    # ----------------------------------
    # Publish Gaspar data to MQTT
    async def publish(self):

        # GrDF configuration
        grdf_username = self._config.get("username")
        grdf_password = self._config.get("password")
        grdf_pce_identifier = str(self._config.get("pce_identifier"))
        grdf_last_days = int(self._config.get("last_days"))
        grdf_timezone = self._config.get("timezone")

        # Initialize PyGazpar client
        client = pygazpar.Client(pygazpar.JsonWebDataSource(username=grdf_username, password=grdf_password))

        try:
            data = client.loadSince(pceIdentifier=grdf_pce_identifier, lastNDays=grdf_last_days, frequencies=[pygazpar.Frequency.DAILY])
        except Exception:
            errorMessage = f"Error while fetching data from GrDF: {traceback.format_exc()}"
            logging.warning(errorMessage)
            data = {}

        # Timezone
        timezone = pytz.timezone(grdf_timezone)

        # Fill statistics.
        daily = data.get(pygazpar.Frequency.DAILY.value)
        statistics = []
        for reading in daily:
            # Parse date format DD/MM/YYYY into datetime.
            date = datetime.strptime(reading[pygazpar.PropertyName.TIME_PERIOD.value], "%d/%m/%Y")
            date = timezone.localize(date)
            statistics.append({
                "start": date.isoformat(),
                "state": reading[pygazpar.PropertyName.END_INDEX.value],
                "sum": reading[pygazpar.PropertyName.END_INDEX.value]
            })

        # Publish statistics to Home Assistant
        try:
            await self._homeassistant.import_statistics(f"sensor.{self._device_name}", "recorder", "gazpar2haws", statistics)
        except Exception:
            errorMessage = f"Error while importing statistics to Home Assistant: {traceback.format_exc()}"
            logging.warning(errorMessage)
