
import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

from bot_config import bot, config
from buttons import cancel_kb, start_kb


logger = logging.getLogger(__name__)
ADMIN_ID = config.tg_bot.ADMIN_ID


class Report(StatesGroup):
    send_report = State()


class ReportAnswer(StatesGroup):
    send_answer = State()


bug_report_callback_info = CallbackData(
    "report_answer", "user_id"
)


async def start_bug_report(message: types.Message):
    """Ask the user to describe a problem."""
    await message.answer(
        "Please describe the problem you encountered.",
        reply_markup=cancel_kb
    )

    await Report.send_report.set()


async def send_report(message: types.Message, state: FSMContext):
    """Forward the user's bug report to the administrator."""
    reply_button = InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            text="Reply",
            callback_data=bug_report_callback_info.new(
                user_id=message.from_user.id
            )
        )
    )

    try:
        await bot.copy_message(
            chat_id=ADMIN_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id,
            reply_markup=reply_button
        )

    except Exception:
        logger.exception("Failed to forward bug report")
        await message.answer(
            "Could not submit your report. Please try again."
        )
        return

    await state.finish()

    await message.answer(
        "Thank you! Your report has been submitted.",
        reply_markup=start_kb
    )


async def get_answer(
    callback_query: types.CallbackQuery,
    callback_data: dict,
    state: FSMContext
):
    """Allow the administrator to reply to a bug report."""
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer(
            "Access denied.",
            show_alert=True
        )
        return

    await state.update_data(
        user_id=int(callback_data["user_id"])
    )

    await ReportAnswer.send_answer.set()

    await callback_query.answer()
    await callback_query.message.answer(
        "Enter your reply to the user:"
    )


async def send_answer(message: types.Message, state: FSMContext):
    """Send the administrator's reply to the user."""
    if message.from_user.id != ADMIN_ID:
        await message.answer("Access denied.")
        return

    data = await state.get_data()
    user_id = data.get("user_id")

    if user_id is None:
        await state.finish()
        await message.answer("No recipient selected.")
        return

    try:
        await bot.send_message(
            chat_id=user_id,
            text=message.text
        )

    except Exception:
        logger.exception("Failed to send administrator reply")
        await message.answer(
            "Could not send the reply. Please try again."
        )
        return

    await state.finish()

    await message.answer(
        "Reply sent successfully.",
        reply_markup=start_kb
    )


def bug_report_register_handlers(dp: Dispatcher):
    """Register bug reporting handlers."""
    dp.register_message_handler(
        start_bug_report,
        commands=["bug_report"]
    )

    dp.register_message_handler(
        send_report,
        state=Report.send_report
    )

    dp.register_message_handler(
        send_answer,
        state=ReportAnswer.send_answer
    )

    dp.register_callback_query_handler(
        get_answer,
        bug_report_callback_info.filter()
    )
