import os
from typing import Any

import yaml


class ConfigLoader:
    def __init__(self, config_file: str, secrets_file: str):
        self.config_file = config_file
        self.secrets_file = secrets_file
        self.config = dict[str, Any]()
        self.secrets = dict[str, Any]()
        self.raw_config = None

    def load_secrets(self):
        """Load the secrets file."""
        if self.secrets_file is None:
            return
        if os.path.exists(self.secrets_file):
            with open(self.secrets_file, "r", encoding="utf-8") as file:
                self.secrets = yaml.safe_load(file)
        else:
            raise FileNotFoundError(f"Secrets file '{self.secrets_file}' not found.")

    def load_config(self):
        """Load the main configuration file and resolve secrets."""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r", encoding="utf-8") as file:
                self.raw_config = yaml.safe_load(file)
            self.config = self._resolve_secrets(self.raw_config)
        else:
            raise FileNotFoundError(f"Configuration file '{self.config_file}' not found.")

    def _resolve_secrets(self, data):
        """Recursively resolve `!secret` keys in the configuration."""
        if isinstance(data, dict):
            return {key: self._resolve_secrets(value) for key, value in data.items()}
        if isinstance(data, list):
            return [self._resolve_secrets(item) for item in data]
        if isinstance(data, str) and data.startswith("!secret"):
            secret_key = data.split(" ", 1)[1]
            if secret_key in self.secrets:
                return self.secrets[secret_key]
            raise KeyError(f"Secret key '{secret_key}' not found in secrets file.")
        return data

    def get(self, key, default=None):
        """Get a configuration value."""
        keys = key.split(".")
        value = self.config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def dict(self) -> dict:
        return self.config

    def dumps(self) -> str:
        return yaml.dump(self.raw_config)
