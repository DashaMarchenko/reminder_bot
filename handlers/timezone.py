
from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot_config import DB


TIMEZONES = {
    "Vienna": "Europe/Vienna",
    "London": "Europe/London",
    "New York": "America/New_York",
    "Bangkok": "Asia/Bangkok",
    "Tokyo": "Asia/Tokyo",
}


async def show_timezone(message: types.Message):
    """Display the current timezone and available options."""
    current_timezone = DB.get_user_timezone(message.from_user.id)

    keyboard = InlineKeyboardMarkup(row_width=2)

    for city, timezone_name in TIMEZONES.items():
        keyboard.insert(
            InlineKeyboardButton(
                text=city,
                callback_data=f"tz:{timezone_name}"
            )
        )

    await message.answer(
        f"Your current timezone: {current_timezone}\n\n"
        "Select your timezone:",
        reply_markup=keyboard
    )


async def set_timezone(callback_query: types.CallbackQuery):
    """Save the timezone selected by the user."""
    timezone_name = callback_query.data.removeprefix("tz:")

    if timezone_name not in TIMEZONES.values():
        await callback_query.answer(
            "Invalid timezone.",
            show_alert=True
        )
        return

    success = DB.set_user_timezone(
        callback_query.from_user.id,
        timezone_name
    )

    if success:
        await callback_query.answer("Timezone updated!")
        await callback_query.message.edit_text(
            f"Your timezone is now: {timezone_name}"
        )
    else:
        await callback_query.answer(
            "Could not update timezone.",
            show_alert=True
        )


def timezone_register_handlers(dp: Dispatcher):
    """Register timezone command and callback handlers."""
    dp.register_message_handler(
        show_timezone,
        commands=["timezone"],
        state="*"
    )

    dp.register_callback_query_handler(
        set_timezone,
        lambda callback: callback.data
        and callback.data.startswith("tz:"),
        state="*"
    )
