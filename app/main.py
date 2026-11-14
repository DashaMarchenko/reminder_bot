import asyncio
import logging

from aiogram import types, Dispatcher, Bot
from aiogram.types import BotCommand
from aiogram.utils.exceptions import BadRequest
from fastapi import FastAPI

from bot_config import dp, bot, TOKEN, logger, config, DB
from schedule import scheduler

app = FastAPI()
WEBHOOK_PATH = f'/bot/{TOKEN}'
WEBHOOK_URL = config.tg_bot.HOST_URL + WEBHOOK_PATH


async def set_commands(bot: Bot):
    commands = [
    BotCommand(command="/start", description="Start the bot"),
    BotCommand(command="/cancel", description="Cancel current action"),
    BotCommand(command="/bug_report", description="Report a bug"),
    BotCommand(command="/timezone", description="Change your timezone"
),
]

    await bot.set_my_commands(commands)


async def bot_main():
    """Register message handlers and configure bot commands."""
    from handlers import other, bug_report, reminder
    from handlers.timezone import timezone_register_handlers

    logging.info('Bot started')

    bug_report(dp)
    other(dp)
    reminder(dp)
    timezone_register_handlers(dp)

    await set_commands(bot)


@app.on_event("startup")
async def on_startup():
    """Register bot handlers, configure the webhook, and start the scheduler."""
    await bot_main()

    try:
        webhook_info = await bot.get_webhook_info()

        if webhook_info.url != WEBHOOK_URL:
            await bot.set_webhook(
                url=WEBHOOK_URL,
                drop_pending_updates=True
            )

        asyncio.create_task(scheduler())

    except BadRequest as ex:
        if "ip address 127.0.0.1 is reserved" in str(ex):
            logging.error("IP address 127.0.0.1 is reserved")
        else:
            logging.error("Webhook setup failed: %s", ex)


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    """Process incoming Telegram updates
    :param update: Telegram update
    :return:
    """
    telegram_update = types.Update(**update)
    Dispatcher.set_current(dp)
    Bot.set_current(bot)
    await dp.process_update(telegram_update)


@app.on_event('shutdown')
async def on_shutdown():
    """
    Close bot resources and remove the webhook
    """
    await dp.storage.close()
    await dp.storage.wait_closed()
    await bot.session.close()
    await bot.delete_webhook()


@app.get('/')
async def home():
    """
    Return the application status
    """
    return 'Bot is running'
