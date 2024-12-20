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

        self._homeassistant = homeassistant

        # GrDF configuration
        self._name = config.get("name")
        self._username = config.get("username")
        self._password = config.get("password")
        self._pce_identifier = str(config.get("pce_identifier"))
        self._last_days = int(config.get("last_days"))
        self._timezone = config.get("timezone")

    # ----------------------------------
    def name(self):
        return self._name

    # ----------------------------------
    # Publish Gaspar data to Home Assistant WS
    async def publish(self):

        # Check the existence of the sensor in Home Assistant
        try:
            exists_statistic_id = await self._homeassistant.exists_statistic_id(f"sensor.{self._name}", "sum")
        except Exception:
            errorMessage = f"Error while checking the existence of the sensor in Home Assistant: {traceback.format_exc()}"
            logging.warning(errorMessage)
            raise Exception(errorMessage)

        if exists_statistic_id:
            # Get last statistics from GrDF
            try:
                last_statistics = await self._homeassistant.get_last_statistic(f"sensor.{self._name}")
            except Exception:
                errorMessage = f"Error while fetching last statistics from Home Assistant: {traceback.format_exc()}"
                logging.warning(errorMessage)
                raise Exception(errorMessage)

            # Extract the end date of the last statistics from the unix timestamp
            last_date = datetime.fromtimestamp(last_statistics.get("end") / 1000)

            # Compute the number of days since the last statistics
            last_days = (datetime.now() - last_date).days
        else:
            # If the sensor does not exist in Home Assistant, fetch the last days defined in the configuration
            last_days = self._last_days

        # Initialize PyGazpar client
        client = pygazpar.Client(pygazpar.JsonWebDataSource(username=self._username, password=self._password))

        try:
            data = client.loadSince(pceIdentifier=self._pce_identifier, lastNDays=last_days, frequencies=[pygazpar.Frequency.DAILY])
        except Exception:
            errorMessage = f"Error while fetching data from GrDF: {traceback.format_exc()}"
            logging.warning(errorMessage)
            data = {}

        # Timezone
        timezone = pytz.timezone(self._timezone)

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
            await self._homeassistant.import_statistics(f"sensor.{self._name}", "recorder", "gazpar2haws", "m³", statistics)
        except Exception:
            errorMessage = f"Error while importing statistics to Home Assistant: {traceback.format_exc()}"
            logging.warning(errorMessage)
            raise Exception(errorMessage)
