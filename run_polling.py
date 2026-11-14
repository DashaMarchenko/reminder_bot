
import asyncio
import logging

from aiogram import executor

from bot_config import bot, dp
from app.main import bot_main
from schedule import scheduler


logger = logging.getLogger(__name__)

scheduler_task = None


async def on_startup(dispatcher):
    """Initialize handlers and start the reminder scheduler."""
    global scheduler_task

    # Disable the webhook before starting long polling.
    await bot.delete_webhook(drop_pending_updates=True)

    # Register Telegram message and callback handlers.
    await bot_main()

    # Start the reminder scheduler in the background.
    scheduler_task = asyncio.create_task(scheduler())

    logger.info("Reminder Bot started in polling mode")


async def on_shutdown(dispatcher):
    """Stop the scheduler and close Telegram resources."""
    global scheduler_task

    if scheduler_task is not None:
        scheduler_task.cancel()

        try:
            await scheduler_task
        except asyncio.CancelledError:
            pass

        scheduler_task = None

    session = await bot.get_session()
    await session.close()

    logger.info("Reminder Bot stopped")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    executor.start_polling(
        dp,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True
    )
