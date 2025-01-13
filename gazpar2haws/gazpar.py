import logging
import traceback
from datetime import datetime, timedelta
from typing import Any

import pygazpar  # type: ignore
import pytz

from gazpar2haws.haws import HomeAssistantWS, HomeAssistantWSException

Logger = logging.getLogger(__name__)


# ----------------------------------
class Gazpar:

    # ----------------------------------
    def __init__(self, config: dict[str, Any], homeassistant: HomeAssistantWS):

        self._homeassistant = homeassistant

        # GrDF configuration
        self._name = config.get("name")
        self._data_source = config.get("data_source")
        self._username = config.get("username")
        self._password = config.get("password")
        self._pce_identifier = str(config.get("pce_identifier"))
        self._tmp_dir = config.get("tmp_dir")
        self._last_days = int(str(config.get("last_days")))
        self._timezone = str(config.get("timezone"))
        self._reset = bool(config.get("reset"))

        # As of date: YYYY-MM-DD
        as_of_date = config.get("as_of_date")
        if self._data_source is not None and str(self._data_source).lower() == "test":
            self._as_of_date = (
                datetime.now(tz=pytz.timezone(self._timezone))
                if as_of_date is None
                else datetime.strptime(as_of_date, "%Y-%m-%d")
            )
        else:
            self._as_of_date = datetime.now(tz=pytz.timezone(self._timezone))

        # Set the timezone
        timezone = pytz.timezone(self._timezone)
        if self._as_of_date.tzinfo is None:
            self._as_of_date = timezone.localize(self._as_of_date)

    # ----------------------------------
    def name(self):
        return self._name

    # ----------------------------------
    # Publish Gaspar data to Home Assistant WS
    async def publish(self):

        # Volume and energy sensor names.
        volume_sensor_name = f"sensor.{self._name}_volume"
        energy_sensor_name = f"sensor.{self._name}_energy"

        # Eventually reset the sensor in Home Assistant
        if self._reset:
            try:
                await self._homeassistant.clear_statistics(
                    [volume_sensor_name, energy_sensor_name]
                )
            except Exception:
                Logger.warning(
                    f"Error while resetting the sensor in Home Assistant: {traceback.format_exc()}"
                )
                raise

        # Publish volume sensor
        await self._publish_entity(
            volume_sensor_name, pygazpar.PropertyName.VOLUME.value, "m³"
        )
        await self._publish_entity(
            energy_sensor_name, pygazpar.PropertyName.ENERGY.value, "kWh"
        )

    # ----------------------------------
    # Publish a sensor to Home Assistant
    async def _publish_entity(
        self, entity_id: str, property_name: str, unit_of_measurement: str
    ):

        # Find last date, days and value of the entity.
        last_date, last_days, last_value = await self._find_last_date_days_value(
            entity_id
        )

        # Instantiate the right data source.
        data_source = self._create_data_source()

        # Initialize PyGazpar client
        client = pygazpar.Client(data_source)

        try:
            data = client.loadSince(
                pceIdentifier=self._pce_identifier,
                lastNDays=last_days,
                frequencies=[pygazpar.Frequency.DAILY],
            )
        except Exception:  # pylint: disable=broad-except
            Logger.warning(
                f"Error while fetching data from GrDF: {traceback.format_exc()}"
            )
            data = {}

        # Timezone
        timezone = pytz.timezone(self._timezone)

        # Compute and fill statistics.
        daily = data.get(pygazpar.Frequency.DAILY.value)
        statistics = []
        total = last_value
        for reading in daily:
            # Parse date format DD/MM/YYYY into datetime.
            date = datetime.strptime(
                reading[pygazpar.PropertyName.TIME_PERIOD.value], "%d/%m/%Y"
            )

            # Set the timezone
            date = timezone.localize(date)

            # Skip all readings before the last statistic date.
            if date <= last_date:
                Logger.debug(f"Skip date: {date} <= {last_date}")
                continue

            # Compute the total volume and energy
            total += reading[property_name]

            statistics.append({"start": date.isoformat(), "state": total, "sum": total})

        # Publish statistics to Home Assistant
        try:
            await self._homeassistant.import_statistics(
                entity_id, "recorder", "gazpar2haws", unit_of_measurement, statistics
            )
        except Exception:
            Logger.warning(
                f"Error while importing statistics to Home Assistant: {traceback.format_exc()}"
            )
            raise

    # ----------------------------------
    # Create the data source.
    def _create_data_source(self) -> pygazpar.datasource.IDataSource:

        if self._data_source is not None:
            if str(self._data_source).lower() == "test":
                return pygazpar.TestDataSource()

            if str(self._data_source).lower() == "excel":
                return pygazpar.ExcelWebDataSource(
                    username=self._username,
                    password=self._password,
                    tmpDirectory=self._tmp_dir,
                )

        return pygazpar.JsonWebDataSource(
            username=self._username, password=self._password
        )

    # ----------------------------------
    # Find last date, days and value of the entity.
    async def _find_last_date_days_value(
        self, entity_id: str
    ) -> tuple[datetime, int, float]:

        # Check the existence of the sensor in Home Assistant
        try:
            exists_statistic_id = await self._homeassistant.exists_statistic_id(
                entity_id, "sum"
            )
        except Exception:
            Logger.warning(
                f"Error while checking the existence of the sensor in Home Assistant: {traceback.format_exc()}"
            )
            raise

        if exists_statistic_id:
            # Get the last statistic from Home Assistant
            try:
                last_statistic = await self._homeassistant.get_last_statistic(
                    entity_id, self._as_of_date, self._last_days
                )
            except HomeAssistantWSException:
                Logger.warning(
                    f"Error while fetching last statistics from Home Assistant: {traceback.format_exc()}"
                )

            if last_statistic:
                # Extract the end date of the last statistics from the unix timestamp
                last_date = datetime.fromtimestamp(
                    int(str(last_statistic.get("start"))) / 1000,
                    tz=pytz.timezone(self._timezone),
                )

                # Compute the number of days since the last statistics
                last_days = (self._as_of_date - last_date).days

                # Get the last meter value
                last_value = float(str(last_statistic.get("sum")))

                Logger.debug(
                    f"Last date: {last_date}, last days: {last_days}, last value: {last_value}"
                )

                return last_date, last_days, last_value

            Logger.debug(f"No statistics found for the existing sensor {entity_id}.")
        else:
            Logger.debug(f"Sensor {entity_id} does not exist in Home Assistant.")

        # If the sensor does not exist in Home Assistant, fetch the last days defined in the configuration
        last_days = self._last_days

        # Compute the corresponding last_date
        last_date = self._as_of_date - timedelta(days=last_days)

        # If no statistic, the last value is initialized to zero
        last_value = 0

        Logger.debug(
            f"Last date: {last_date}, last days: {last_days}, last value: {last_value}"
        )

        return last_date, last_days, last_value
