
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import CallbackQuery

from bot_config import DB
from buttons import start_kb, cancel_kb, choice_kb
from calendars import simple_calendar_callback, SimpleCalendar


VIENNA_TZ = ZoneInfo("Europe/Vienna")


def localize_time(naive_datetime: datetime, timezone_name: str) -> datetime:
    """Validate a local time, including DST transitions."""
    tz = ZoneInfo(timezone_name)
    candidates = []

    for fold in (0, 1):
        local_dt = naive_datetime.replace(tzinfo=tz, fold=fold)

        round_trip = (
            local_dt.astimezone(timezone.utc)
            .astimezone(tz)
        )

        if round_trip.replace(tzinfo=None) == naive_datetime:
            candidates.append(local_dt)

    if not candidates:
        raise ValueError("This local time does not exist.")

    if candidates[0].utcoffset() != candidates[-1].utcoffset():
        raise ValueError("This local time is ambiguous.")

    return candidates[0]


def localize_vienna_time(naive_datetime: datetime) -> datetime:
    """Validate Vienna local time for backward compatibility."""
    return localize_time(naive_datetime, "Europe/Vienna")


class ReminderState(StatesGroup):
    choosing_date = State()
    entering_time = State()
    entering_text = State()
    confirming = State()


async def start_mess(message: types.Message):
    """Welcome the user."""
    await message.answer(
        f"Hi, {message.from_user.first_name}! "
        "I can remind you about important events.",
        reply_markup=start_kb
    )


async def send_calendar(message: types.Message, state: FSMContext):
    """Display a calendar for selecting a reminder date."""
    await state.finish()

    await message.answer(
        "Choose the date for your reminder:",
        reply_markup=await SimpleCalendar().start_calendar()
    )

    await ReminderState.choosing_date.set()


async def send_question(
    callback_query: CallbackQuery,
    callback_data: dict,
    state: FSMContext
):
    """Process the selected date and ask for a time."""
    selected, date = await SimpleCalendar().process_selection(
        callback_query, callback_data
    )

    if not selected:
        return

    user_timezone = DB.get_user_timezone(callback_query.from_user.id)
    user_tz = ZoneInfo(user_timezone)

    if date.date() < datetime.now(user_tz).date():
        await callback_query.message.answer(
            "This date is in the past. Please choose another date."
        )
        return

    async with state.proxy() as data:
        data["date"] = date.strftime("%d.%m.%Y")

    await callback_query.message.answer(
        "Enter the reminder time in HH:MM format.\n"
        "Example: 08:52",
        reply_markup=cancel_kb
    )

    await ReminderState.entering_time.set()



async def get_info(message: types.Message, state: FSMContext):
    """Validate the user's local time and convert it to UTC."""
    data = await state.get_data()
    selected_date = data.get("date")

    user_timezone = DB.get_user_timezone(message.from_user.id)
    user_tz = ZoneInfo(user_timezone)

    try:
        # Combine the selected date and entered time.
        naive_datetime = datetime.strptime(
            f"{selected_date} {message.text.strip()}",
            "%d.%m.%Y %H:%M"
        )

    except (ValueError, AttributeError, TypeError):
        await message.answer(
            "Invalid time format. Please use HH:MM.\n"
            "Example: 14:30",
            reply_markup=cancel_kb
        )
        return

    try:
        # Validate the local time, including DST transitions.
        local_datetime = localize_time(
            naive_datetime,
            user_timezone
        )

    except ValueError:
        await message.answer(
            "This time is invalid or ambiguous due to "
            "daylight saving time changes. "
            "Please choose another time.",
            reply_markup=cancel_kb
        )
        return

    if local_datetime <= datetime.now(user_tz):
        await message.answer(
            "This date and time are in the past. "
            "Please enter a future time.",
            reply_markup=cancel_kb
        )
        return

    # Convert the selected local time to UTC.
    utc_datetime = local_datetime.astimezone(timezone.utc)

    async with state.proxy() as data:
        data["all_date"] = utc_datetime.isoformat()
        data["display_date"] = local_datetime.strftime(
            "%d.%m.%Y %H:%M"
        )
        data["timezone"] = user_timezone

    await message.answer(
        "Enter the reminder text:",
        reply_markup=cancel_kb
    )

    await ReminderState.entering_text.set()



async def get_text(message: types.Message, state: FSMContext):
    """Store the reminder text and request confirmation."""
    if not message.text or not message.text.strip():
        await message.answer(
            "Please enter a non-empty reminder."
        )
        return

    async with state.proxy() as data:
        data["text"] = message.text.strip()

    data = await state.get_data()

    await message.answer(
        "Is everything correct?\n\n"
        f"Date: {data['display_date']} ({data['timezone']})\n"
        f"Reminder: {data['text']}",
        reply_markup=choice_kb
    )

    await ReminderState.confirming.set()


async def save_info(message: types.Message, state: FSMContext):
    """Save the confirmed reminder to the database."""
    answer = message.text.strip().lower()

    if answer == "no":
        await state.finish()
        await message.answer(
            "Reminder cancelled.",
            reply_markup=start_kb
        )
        return

    if answer != "yes":
        await message.answer(
            "Please select Yes, No, or Cancel.",
            reply_markup=choice_kb
        )
        return

    data = await state.get_data()

    result = DB.insert_one_value(
        user_id=message.from_user.id,
        name=message.from_user.first_name,
        date=data["all_date"],
        text=data["text"]
    )

    await state.finish()

    if result[0]:
        await message.answer(
            "Reminder saved successfully!",
            reply_markup=start_kb
        )
    else:
        await message.answer(
            "Failed to save the reminder. Please try again.",
            reply_markup=start_kb
        )


def remind_register_handlers(dp: Dispatcher):
    """Register reminder conversation handlers."""
    dp.register_message_handler(
        start_mess,
        commands=["start"],
        state="*"
    )

    dp.register_message_handler(
        send_calendar,
        Text(equals="Add reminder", ignore_case=True),
        state="*"
    )

    dp.register_callback_query_handler(
        send_question,
        simple_calendar_callback.filter(),
        state=ReminderState.choosing_date
    )

    dp.register_message_handler(
        get_info,
        state=ReminderState.entering_time
    )

    dp.register_message_handler(
        get_text,
        state=ReminderState.entering_text
    )

    dp.register_message_handler(
        save_info,
        state=ReminderState.confirming
    )
