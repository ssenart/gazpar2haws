import asyncio
import logging
import signal

from gazpar2haws import config_utils
from gazpar2haws.gazpar import Gazpar
from gazpar2haws.haws import HomeAssistantWS

Logger = logging.getLogger(__name__)


# ----------------------------------
class Bridge:

    # ----------------------------------
    def __init__(self, config: config_utils.ConfigLoader):

        # GrDF scan interval (in seconds)
        self._grdf_scan_interval = int(config.get("grdf.scan_interval"))

        # Home Assistant configuration
        ha_host = config.get("homeassistant.host")
        ha_port = config.get("homeassistant.port")
        ha_endpoint = config.get("homeassistant.endpoint")
        ha_token = config.get("homeassistant.token")

        # Initialize Home Assistant
        self._homeassistant = HomeAssistantWS(ha_host, ha_port, ha_endpoint, ha_token)

        # Initialize Gazpar
        self._gazpar = []
        for grdf_device_config in config.get("grdf.devices"):
            self._gazpar.append(Gazpar(grdf_device_config, self._homeassistant))

        # Set up signal handler
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)

        # Initialize running flag
        self._running = False

    # ----------------------------------
    # Graceful shutdown function
    def handle_signal(self, signum, _):
        print(f"Signal {signum} received. Shutting down gracefully...")
        Logger.info(f"Signal {signum} received. Shutting down gracefully...")
        self._running = False

    # ----------------------------------
    async def run(self):

        # Set running flag
        self._running = True

        try:
            while self._running:

                # Connect to Home Assistant
                await self._homeassistant.connect()

                # Publish Gazpar data to Home Assistant WS
                Logger.info("Publishing Gazpar data to Home Assistant WS...")

                for gazpar in self._gazpar:
                    Logger.info(f"Publishing data for device '{gazpar.name()}'...")
                    await gazpar.publish()
                    Logger.info(
                        f"Device '{gazpar.name()}' data published to Home Assistant WS."
                    )

                Logger.info("Gazpar data published to Home Assistant WS.")

                # Disconnect from Home Assistant
                await self._homeassistant.disconnect()

                # Wait before next scan
                Logger.info(
                    f"Waiting {self._grdf_scan_interval} minutes before next scan..."
                )

                # Check if the scan interval is 0 and leave the loop.
                if self._grdf_scan_interval == 0:
                    break

                await self._await_with_interrupt(self._grdf_scan_interval * 60, 5)
        except KeyboardInterrupt:
            print("Keyboard interrupt detected. Shutting down gracefully...")
            Logger.info("Keyboard interrupt detected. Shutting down gracefully...")

    # ----------------------------------
    async def _await_with_interrupt(self, total_sleep_time: int, check_interval: int):
        elapsed_time = 0
        while elapsed_time < total_sleep_time:
            await asyncio.sleep(check_interval)
            elapsed_time += check_interval
            # Check if an interrupt signal or external event requires breaking
            if not self._running:  # Assuming `running` is a global flag
                break
