from pydantic import BaseModel

from gazpar2haws import config_utils
from gazpar2haws.model import Grdf, HomeAssistant, Logging, Pricing


class Configuration(BaseModel):

    logging: Logging
    grdf: Grdf
    homeassistant: HomeAssistant
    pricing: Pricing

    @classmethod
    def load(cls, config_file: str, secrets_file: str):

        # Load configuration
        config = config_utils.ConfigLoader(config_file, secrets_file)
        config.load_secrets()
        config.load_config()

        return cls(**config.dict())
