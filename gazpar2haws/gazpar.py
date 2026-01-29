import logging
import traceback
from datetime import date, datetime, timedelta
from typing import Optional

import pygazpar  # type: ignore
import pytz
from pygazpar.datasource import MeterReadings  # type: ignore

from gazpar2haws.date_array import DateArray
from gazpar2haws.datetime_utils import timestamp_ms_to_date
from gazpar2haws.haws import HomeAssistantWS, HomeAssistantWSException
from gazpar2haws.model import (
    ConsumptionQuantityArray,
    Device,
    PriceUnit,
    Pricing,
    QuantityUnit,
    TimeUnit,
)
from gazpar2haws.pricer import Pricer

Logger = logging.getLogger(__name__)


# ----------------------------------
class Gazpar:

    # ----------------------------------
    def __init__(
        self,
        device_config: Device,
        pricing_config: Optional[Pricing],
        homeassistant: HomeAssistantWS,
    ):

        self._homeassistant = homeassistant
        self._grdf_config = device_config
        self._pricing_config = pricing_config

        # GrDF configuration: name
        self._name = device_config.name

        # GrDF configuration: data source
        self._data_source = device_config.data_source

        # GrDF configuration: username
        self._username = device_config.username

        # GrDF configuration: password
        self._password = device_config.password.get_secret_value() if device_config.password is not None else None

        # GrDF configuration: pce_identifier
        self._pce_identifier = (
            device_config.pce_identifier.get_secret_value() if device_config.pce_identifier is not None else None
        )

        # GrDF configuration: tmp_dir
        self._tmp_dir = device_config.tmp_dir

        # GrDF configuration: last_days
        self._last_days = device_config.last_days

        # GrDF configuration: timezone
        self._timezone = device_config.timezone

        # GrDF configuration: reset
        self._reset = device_config.reset

        # As of date: YYYY-MM-DD
        self._as_of_date = device_config.as_of_date

        # Set the timezone
        self._timezone = device_config.timezone

    # ----------------------------------
    def name(self):
        return self._name

    # ----------------------------------
    def as_of_date(self):
        return date.today() if self._as_of_date is None else self._as_of_date

    # ----------------------------------
    # Publish Gaspar data to Home Assistant WS
    async def publish(self):  # pylint: disable=too-many-branches, too-many-statements

        # As of date
        as_of_date = self.as_of_date()
        Logger.debug(f"As of date: {as_of_date}")

        # Volume, energy and cost sensor names.
        volume_sensor_name = f"sensor.{self._name}_volume"
        energy_sensor_name = f"sensor.{self._name}_energy"
        total_cost_sensor_name = f"sensor.{self._name}_total_cost"

        # Generate component cost sensor names dynamically
        component_sensor_names = {}
        if self._pricing_config is not None:
            for component_name in self._pricing_config.get_components().keys():
                sensor_suffix = self._get_legacy_sensor_suffix(component_name)
                sensor_name = f"sensor.{self._name}_{sensor_suffix}"
                component_sensor_names[component_name] = sensor_name

        # Automatic migration from v0.3.x to v0.4.0
        # Migrate old sensor.{name}_cost to sensor.{name}_total_cost if pricing is enabled
        if self._pricing_config is not None:
            try:
                old_total_cost_sensor_name = f"sensor.{self._name}_cost"
                await self._homeassistant.migrate_statistic(
                    old_entity_id=old_total_cost_sensor_name,
                    new_entity_id=total_cost_sensor_name,
                    new_name="Gazpar2HAWS Total Cost",
                    unit_class=None,
                    unit_of_measurement=self._convert_euro_symbol_to_iso4217("€"),
                    timezone=self._timezone,
                    as_of_date=as_of_date,
                )
            except Exception:  # pylint: disable=broad-except
                Logger.warning(
                    f"Error during automatic sensor migration from "
                    f"{old_total_cost_sensor_name} to {total_cost_sensor_name}: "
                    f"{traceback.format_exc()}"
                )

        # Eventually reset the sensor in Home Assistant
        if self._reset:
            try:
                sensors_to_clear = [volume_sensor_name, energy_sensor_name, total_cost_sensor_name]
                # Add all component cost sensors dynamically
                sensors_to_clear.extend(component_sensor_names.values())
                await self._homeassistant.clear_statistics(sensors_to_clear)
            except Exception:
                Logger.warning(f"Error while resetting the sensor in Home Assistant: {traceback.format_exc()}")
                raise

        last_date_and_value_by_sensor = dict[str, tuple[date, float]]()

        last_date_and_value_by_sensor[volume_sensor_name] = await self.find_last_date_and_value(volume_sensor_name)
        last_date_and_value_by_sensor[energy_sensor_name] = await self.find_last_date_and_value(energy_sensor_name)
        last_date_and_value_by_sensor[total_cost_sensor_name] = await self.find_last_date_and_value(
            total_cost_sensor_name
        )

        # Get last date and value for all component cost sensors dynamically
        for sensor_name in component_sensor_names.values():
            last_date_and_value_by_sensor[sensor_name] = await self.find_last_date_and_value(sensor_name)

        # Compute the start date as the minimum of the last dates plus one day
        start_date = min(min(v[0] for v in last_date_and_value_by_sensor.values()) + timedelta(days=1), as_of_date)

        # Get all start dates
        energy_start_date = last_date_and_value_by_sensor[energy_sensor_name][0] + timedelta(days=1)
        volume_start_date = last_date_and_value_by_sensor[volume_sensor_name][0] + timedelta(days=1)
        total_cost_start_date = last_date_and_value_by_sensor[total_cost_sensor_name][0] + timedelta(days=1)

        # Get the minimum cost start date from all component sensors
        cost_start_dates = [total_cost_start_date]
        for sensor_name in component_sensor_names.values():
            cost_start_dates.append(last_date_and_value_by_sensor[sensor_name][0] + timedelta(days=1))
        cost_start_date = min(cost_start_dates)

        Logger.debug(f"Min start date for all sensors: {start_date}")
        Logger.debug(f"Energy start date: {energy_start_date}")
        Logger.debug(f"Volume start date: {volume_start_date}")
        Logger.debug(f"Total cost start date: {total_cost_start_date}")
        Logger.debug(f"Min cost start date: {cost_start_date}")

        # Fetch the data from GrDF and publish it to Home Assistant
        daily_history = self.fetch_daily_gazpar_history(start_date, as_of_date)

        # The end date is the last date of the daily history
        if daily_history is None or len(daily_history) == 0:
            end_date = start_date
        else:
            end_date = datetime.strptime(daily_history[-1][pygazpar.PropertyName.TIME_PERIOD.value], "%d/%m/%Y").date()

        Logger.debug(f"End date: {end_date}")

        # Extract the volume from the daily history
        volume_array = self.extract_property_from_daily_gazpar_history(
            daily_history,
            pygazpar.PropertyName.VOLUME.value,
            volume_start_date,
            end_date,
        )

        # Extract the energy from the daily history
        energy_array = self.extract_property_from_daily_gazpar_history(
            daily_history,
            pygazpar.PropertyName.ENERGY.value,
            min(energy_start_date, cost_start_date),
            end_date,
        )

        # Publish the volume and energy to Home Assistant
        if volume_array is not None:
            await self.publish_date_array(
                volume_sensor_name,
                "Gazpar2HAWS Volume",
                "volume",
                "m³",
                volume_array,
                last_date_and_value_by_sensor[volume_sensor_name][1],
            )
        else:
            Logger.info("No volume data to publish")

        if energy_array is not None and energy_start_date <= end_date:
            await self.publish_date_array(
                energy_sensor_name,
                "Gazpar2HAWS Energy",
                "energy",
                "kWh",
                energy_array[energy_start_date : end_date + timedelta(days=1)],
                last_date_and_value_by_sensor[energy_sensor_name][1],
            )
        else:
            Logger.info("No energy data to publish")

        if self._pricing_config is None:
            Logger.info("No pricing configuration provided")
            return

        # Compute the cost from the energy
        if energy_array is not None:
            pricer = Pricer(self._pricing_config)

            quantities = ConsumptionQuantityArray(
                start_date=cost_start_date,
                end_date=end_date,
                value_unit=QuantityUnit.KWH,
                base_unit=TimeUnit.DAY,
                value_array=energy_array[cost_start_date : end_date + timedelta(days=1)],
            )

            # Price all the costs and require results in Euro.
            cost_breakdown = pricer.compute(quantities, PriceUnit.EURO)
        else:
            cost_breakdown = None

        # Publish the cost breakdown to Home Assistant
        if cost_breakdown is not None:
            # Publish all component costs dynamically
            component_costs = cost_breakdown.get_component_costs()
            for component_name, component_cost in component_costs.items():
                sensor_name = component_sensor_names[component_name]
                friendly_name = self._generate_friendly_name(component_name)

                await self.publish_date_array(
                    sensor_name,
                    friendly_name,
                    None,
                    self._convert_euro_symbol_to_iso4217(component_cost.value_unit),
                    component_cost.value_array,
                    last_date_and_value_by_sensor[sensor_name][1],
                )

            # Publish total cost
            await self.publish_date_array(
                total_cost_sensor_name,
                "Gazpar2HAWS Total Cost",
                None,
                self._convert_euro_symbol_to_iso4217(cost_breakdown.total.value_unit),
                cost_breakdown.total.value_array,
                last_date_and_value_by_sensor[total_cost_sensor_name][1],
            )
        else:
            Logger.info("No cost data to publish")

    # ----------------------------------
    # Fetch daily Gazpar history.
    def fetch_daily_gazpar_history(self, start_date: date, end_date: date) -> MeterReadings:

        if start_date >= end_date:
            Logger.info("No data to fetch")
            return []

        # Instantiate the right data source.
        data_source = self._create_data_source()

        # Initialize PyGazpar client
        client = pygazpar.Client(data_source)

        try:
            history = client.load_date_range(
                pce_identifier=self._pce_identifier,
                start_date=start_date,
                end_date=end_date,
                frequencies=[pygazpar.Frequency.DAILY],
            )

            # Filter the daily readings by keeping only dates between start_date and end_date
            res = []
            for reading in history[pygazpar.Frequency.DAILY.value]:
                reading_date = datetime.strptime(reading[pygazpar.PropertyName.TIME_PERIOD.value], "%d/%m/%Y").date()
                if start_date <= reading_date <= end_date:
                    res.append(reading)

            Logger.debug(f"Fetched {len(res)} daily readings from start date {start_date} to end date {end_date}")
        except Exception:  # pylint: disable=broad-except
            Logger.warning(f"Error while fetching data from GrDF: {traceback.format_exc()}")
            res = MeterReadings()

        return res

    # ----------------------------------
    # Extract a given property from the daily Gazpar history and return a DateArray.
    def extract_property_from_daily_gazpar_history(
        self,
        readings: MeterReadings,
        property_name: str,
        start_date: date,
        end_date: date,
    ) -> Optional[DateArray]:

        # Fill the quantity array.
        res: Optional[DateArray] = None

        for reading in readings:
            # Parse date format DD/MM/YYYY into datetime.
            reading_date = datetime.strptime(reading[pygazpar.PropertyName.TIME_PERIOD.value], "%d/%m/%Y").date()

            # Skip all readings before the start date.
            if reading_date < start_date:
                # Logger.debug(f"Skip date: {reading_date} < {start_date}")
                continue

            # Skip all readings after the end date.
            if reading_date > end_date:
                # Logger.debug(f"Skip date: {reading_date} > {end_date}")
                continue

            # Fill the quantity array.
            if reading[property_name] is not None:
                if res is None:
                    res = DateArray(name=property_name, start_date=start_date, end_date=end_date)
                res[reading_date] = reading[property_name]

        return res

    # ----------------------------------
    # Push a date array to Home Assistant.
    async def publish_date_array(
        self,
        entity_id: str,
        entity_name: str,
        unit_class: str | None,
        unit_of_measurement: str,
        date_array: DateArray,
        initial_value: float,
    ):

        # Compute the cumulative sum of the values.
        total_array = date_array.cumsum() + initial_value

        # Timezone
        timezone = pytz.timezone(self._timezone)

        # Fill the statistics.
        statistics = []
        for dt, total in total_array:
            # Set the timezone
            date_time = datetime.combine(dt, datetime.min.time())
            date_time = timezone.localize(date_time)
            statistics.append({"start": date_time.isoformat(), "state": total, "sum": total})

        # Publish statistics to Home Assistant
        try:
            await self._homeassistant.import_statistics(
                entity_id, "recorder", entity_name, unit_class, unit_of_measurement, statistics
            )
        except Exception:
            Logger.warning(f"Error while importing statistics to Home Assistant: {traceback.format_exc()}")
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

        return pygazpar.JsonWebDataSource(username=self._username, password=self._password)

    # ----------------------------------
    # Find last date, value of the entity.
    async def find_last_date_and_value(self, entity_id: str) -> tuple[date, float]:

        # As of date
        as_of_date = self.as_of_date()

        # Check the existence of the sensor in Home Assistant
        try:
            exists_statistic_id = await self._homeassistant.exists_statistic_id(entity_id, "sum")
        except Exception:
            Logger.warning(
                f"Error while checking the existence of the entity '{entity_id}' in Home Assistant: {traceback.format_exc()}"
            )
            raise

        if exists_statistic_id:
            # Get the last statistic from Home Assistant
            try:
                as_of_datetime = datetime.combine(as_of_date, datetime.min.time())
                as_of_datetime = pytz.timezone(self._timezone).localize(as_of_datetime)

                last_statistic = await self._homeassistant.get_last_statistic(
                    entity_id, as_of_datetime, self._last_days
                )
            except HomeAssistantWSException:
                Logger.warning(
                    f"Error while fetching last statistics of the entity '{entity_id}' from Home Assistant: {traceback.format_exc()}"
                )

            if last_statistic:
                # Extract the end date of the last statistics from the unix timestamp
                last_date = timestamp_ms_to_date(last_statistic.get("start"), self._timezone)  # type: ignore[arg-type]

                # Get the last meter value
                last_value = float(str(last_statistic.get("sum")))

                Logger.debug(f"Entity '{entity_id}' => Last date: {last_date}, last value: {last_value}")

                return last_date, last_value

            Logger.debug(f"Entity '{entity_id}' => No statistics found.")
        else:
            Logger.debug(f"Entity '{entity_id}' does not exist in Home Assistant.")

        # Compute the corresponding last_date
        last_date = as_of_date - timedelta(days=self._last_days)

        # If no statistic, the last value is initialized to zero
        last_value = 0

        Logger.debug(f"Entity '{entity_id}' => Last date: {last_date}, last value: {last_value}")

        return last_date, last_value

    # ---------------------------------
    # Helper methods for dynamic sensor naming
    @staticmethod
    def _get_legacy_sensor_suffix(component_name: str) -> str:
        """
        Map component names to sensor suffixes for backward compatibility.

        Legacy component names get their specific sensor suffixes to maintain
        backward compatibility with existing Home Assistant sensors.
        Custom component names get a '_cost' suffix.

        Args:
            component_name: The pricing component name

        Returns:
            The sensor suffix to use
        """
        legacy_map = {
            "consumption_prices": "consumption_cost",
            "subscription_prices": "subscription_cost",
            "transport_prices": "transport_cost",
            "energy_taxes": "energy_taxes_cost",
        }
        return legacy_map.get(component_name, f"{component_name}_cost")

    @staticmethod
    def _generate_friendly_name(component_name: str) -> str:
        """
        Convert component name to friendly sensor name for Home Assistant.

        Legacy component names get their traditional friendly names.
        Custom component names are converted from snake_case to Title Case.

        Args:
            component_name: The pricing component name

        Returns:
            The friendly name for the sensor
        """
        legacy_friendly = {
            "consumption_prices": "Gazpar2HAWS Consumption Cost",
            "subscription_prices": "Gazpar2HAWS Subscription Cost",
            "transport_prices": "Gazpar2HAWS Transport Cost",
            "energy_taxes": "Gazpar2HAWS Energy Taxes Cost",
        }
        if component_name in legacy_friendly:
            return legacy_friendly[component_name]

        # Custom names: convert snake_case to Title Case
        words = component_name.replace("_", " ").title()
        return f"Gazpar2HAWS {words} Cost"

    # Convert Euro symbol to ISO 4217 code (EUR)
    @staticmethod
    def _convert_euro_symbol_to_iso4217(currency_symbol: str) -> str:
        """
        Convert Euro symbol (€) to ISO 4217 code (EUR) for Home Assistant.

        This maintains separation between the domain model (which uses €)
        and the Home Assistant integration (which requires ISO 4217 codes).

        Note: Only Euro is currently supported as this is what the pricer
        module returns when called with PriceUnit.EURO.

        Args:
            currency_symbol: Euro symbol (€)

        Returns:
            ISO 4217 currency code (EUR)

        Raises:
            ValueError: If currency_symbol is not €
        """
        if currency_symbol == "€":
            return "EUR"

        raise ValueError(f"Unexpected currency symbol: {currency_symbol}. Only € (Euro) is supported.")
