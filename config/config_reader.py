
import configparser
from dataclasses import dataclass


@dataclass
class Bot:
    BOT_TOKEN: str
    HOST_URL: str
    ADMIN_ID: int


@dataclass
class Config:
    tg_bot: Bot


def load_config(path: str) -> Config:
    """Load bot settings from an INI configuration file."""
    config = configparser.ConfigParser()

    if not config.read(path):
        raise FileNotFoundError(
            f"Configuration file not found: {path}"
        )

    settings = config["BOT_CONFIG"]

    return Config(
        tg_bot=Bot(
            BOT_TOKEN=settings["BOT_TOKEN"],
            HOST_URL=settings["HOST_URL"],
            ADMIN_ID=int(settings["ADMIN_ID"])
        )
    )
