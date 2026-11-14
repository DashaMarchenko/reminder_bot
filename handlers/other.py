
import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from buttons import start_kb


async def cancel(message: types.Message, state: FSMContext):
    """Cancel the current conversation state."""
    current_state = await state.get_state()

    if current_state is None:
        return

    logging.info("Cancelling state %s", current_state)

    await state.finish()
    await message.reply(
        "Action cancelled.",
        reply_markup=start_kb
    )


def other_register_handlers(dp: Dispatcher):
    """Register cancellation handlers."""
    dp.register_message_handler(
        cancel,
        commands=["cancel"],
        state="*"
    )

    dp.register_message_handler(
        cancel,
        Text(equals="Cancel", ignore_case=True),
        state="*"
    )
