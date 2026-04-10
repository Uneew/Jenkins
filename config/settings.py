import os
import yaml


class Config:
    def __init__(self):
        self.env = os.getenv("TEST_ENV", "test")
        with open("config/env.yaml", "r", encoding="utf-8") as f:
            self.env_config = yaml.safe_load(f)[self.env]

        self.BASE_URL = self.env_config["base_url"]
        self.TIMEOUT = self.env_config["timeout"]
        self.HEADERS = {
            "Content-Type": "application/json",
            "User-Agent": "AutoTest-Client/1.0"
        }


config = Config()