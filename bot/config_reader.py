from dataclasses import dataclass
from os import getenv



@dataclass
class Bot:
    token: str = getenv("TELEGRAM_API_KEY")
    admin: str = getenv("ADMIN_ID")

@dataclass
class Configuration:
    bot = Bot()


conf = Configuration()
