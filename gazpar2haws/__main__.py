import argparse
import asyncio
import logging
import traceback

from gazpar2haws import __version__, config_utils
from gazpar2haws.bridge import Bridge

Logger = logging.getLogger(__name__)


# ----------------------------------
async def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        prog="gazpar2haws",
        description="Gateway that reads data history from the GrDF (French gas provider) meter and send it to Home Assistant using WebSocket interface.",
    )
    parser.add_argument(
        "-v", "--version", action="version", version="Gazpar2HAWS version"
    )
    parser.add_argument(
        "-c",
        "--config",
        required=False,
        default="config/configuration.yaml",
        help="Path to the configuration file",
    )
    parser.add_argument(
        "-s",
        "--secrets",
        required=False,
        default="config/secrets.yaml",
        help="Path to the secret file",
    )

    args = parser.parse_args()

    try:
        # Load configuration files
        config = config_utils.ConfigLoader(args.config, args.secrets)
        config.load_secrets()
        config.load_config()

        print(f"Gazpar2HAWS version: {__version__}")

        # Set up logging
        logging_file = config.get("logging.file")
        logging_console = bool(config.get("logging.console"))
        logging_level = config.get("logging.level")
        logging_format = config.get("logging.format")

        # Convert logging level to integer
        if logging_level.upper() == "DEBUG":
            level = logging.DEBUG
        elif logging_level.upper() == "INFO":
            level = logging.INFO
        elif logging_level.upper() == "WARNING":
            level = logging.WARNING
        elif logging_level.upper() == "ERROR":
            level = logging.ERROR
        elif logging_level.upper() == "CRITICAL":
            level = logging.CRITICAL
        else:
            level = logging.INFO

        logging.basicConfig(filename=logging_file, level=level, format=logging_format)

        if logging_console:
            # Add a console handler manually
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)  # Set logging level for the console
            console_handler.setFormatter(
                logging.Formatter(logging_format)
            )  # Customize console format

            # Get the root logger and add the console handler
            logging.getLogger().addHandler(console_handler)

        Logger.info(f"Starting Gazpar2HAWS version {__version__}")

        # Log configuration
        Logger.info(f"Configuration:\n{config.dumps()}")

        # Start the bridge
        bridge = Bridge(config)
        await bridge.run()

        Logger.info("Gazpar2HAWS stopped.")

        return 0

    except Exception:  # pylint: disable=broad-except
        errorMessage = (
            f"An error occured while running Gazpar2HAWS: {traceback.format_exc()}"
        )
        Logger.error(errorMessage)
        print(errorMessage)
        return 1


# ----------------------------------
if __name__ == "__main__":
    asyncio.run(main())
