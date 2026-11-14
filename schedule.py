
import asyncio
import logging

from bot_config import bot, DB


logger = logging.getLogger(__name__)


async def send_reminder():
    """Send due reminders and delete them after delivery."""
    reminders = DB.send_remind()

    for remind in reminders:
        try:
            await bot.send_message(
                remind.user_id,
                f"{remind.name}, here's your reminder:\n\n{remind.text}"
            )

            if not DB.delete_reminder(remind.id):
                logger.error(
                    "Reminder %s was sent but could not be deleted",
                    remind.id
                )

        except Exception:
            logger.exception(
                "Failed to send reminder %s",
                remind.id
            )



async def scheduler():
    """Check for due reminders until the task is cancelled."""
    logger.info("Reminder scheduler started")

    try:
        while True:
            try:
                await send_reminder()
            except Exception:
                logger.exception("Unexpected scheduler error")

            await asyncio.sleep(10)

    except asyncio.CancelledError:
        logger.info("Reminder scheduler stopped")
        raise
