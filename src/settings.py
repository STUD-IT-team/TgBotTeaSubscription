from __future__ import annotations

import configparser
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = configparser.ConfigParser()
config.read(os.path.join(BASE_DIR, "config.cfg"))


class Settings:
    def __init__(self) -> None:
        app = config["app"]

        self.DATABASE_URL_ASYNC: str = app["DATABASE_URL_ASYNC"]


settings = Settings()
