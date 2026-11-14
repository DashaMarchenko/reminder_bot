import logging
from functools import wraps
from pathlib import Path

from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from cachetools import TTLCache

from config import load_config
from database.sqlite_db import SQLiteDB


storage = MemoryStorage()
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config" / "config.ini"

config = load_config(str(CONFIG_PATH))

TOKEN = config.tg_bot.BOT_TOKEN
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)

DB = SQLiteDB()


def antispam(
    rate: int,
    interval: int,
    mess: str = "Too many requests. Please try again later."
):
    """
    Limit the number of messages a user can send within a time interval.

    Args:
        rate: Maximum number of allowed messages per user.
        interval: Time interval in seconds.
        mess: Message sent when the rate limit is exceeded.
    """
    cache = TTLCache(maxsize=1000, ttl=interval)

    def decorator(func):
        @wraps(func)
        async def wrapped(
            message: types.Message,
            state: FSMContext,
            *args,
            **kwargs
        ):
            user_id = message.from_user.id

            if user_id in cache:
                if cache[user_id] >= rate:
                    await message.reply(mess)
                    return

                cache[user_id] += 1
            else:
                cache[user_id] = 1

            return await func(message, state, *args, **kwargs)

        return wrapped

    return decorator