
import unittest
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch
from types import SimpleNamespace
from zoneinfo import ZoneInfo

from handlers.reminder import (
    ReminderState,
    get_info,
    get_text,
    save_info,
)


class FakeState:
    """Simulate FSM data storage without Telegram."""

    def __init__(self, date):
        self.data = {"date": date}
        self.finish = AsyncMock()

    async def get_data(self):
        return self.data.copy()

    @asynccontextmanager
    async def proxy(self):
        yield self.data


def make_message(text):
    """Create a fake Telegram message."""
    return SimpleNamespace(
        text=text,
        from_user=SimpleNamespace(
            id=12345,
            first_name="Alice"
        ),
        answer=AsyncMock()
    )


class TestReminderFlow(unittest.IsolatedAsyncioTestCase):

    async def test_create_reminder(self):
        """Test time, text, confirmation, and database storage."""

        vienna = ZoneInfo("Europe/Vienna")
        tomorrow = datetime.now(vienna) + timedelta(days=1)
        date = tomorrow.strftime("%d.%m.%Y")

        state = FakeState(date)

        with (
            patch.object(
                ReminderState.entering_text,
                "set",
                new_callable=AsyncMock
            ),
            patch.object(
                ReminderState.confirming,
                "set",
                new_callable=AsyncMock
            ),
            patch(
                "handlers.reminder.DB.insert_one_value",
                return_value=(True, 200, ())
            ) as mock_insert
        ):

            # Step 1: Enter reminder time.
            await get_info(make_message("14:30"), state)

            self.assertIn("all_date", state.data)
            self.assertIn("display_date", state.data)

            # Step 2: Enter reminder text.
            await get_text(
                make_message("Study Python"),
                state
            )

            self.assertEqual(
                state.data["text"],
                "Study Python"
            )

            # Step 3: Confirm and save.
            await save_info(make_message("Yes"), state)

            mock_insert.assert_called_once()

            kwargs = mock_insert.call_args.kwargs

            self.assertEqual(kwargs["user_id"], 12345)
            self.assertEqual(kwargs["text"], "Study Python")

            # Check that the stored timestamp is UTC.
            stored_date = datetime.fromisoformat(
                kwargs["date"]
            )

            self.assertEqual(
                stored_date.utcoffset(),
                timedelta(0)
            )

            self.assertEqual(stored_date.hour, 13 if
                tomorrow.utcoffset() == timedelta(hours=1)
                else 12
            )

            state.finish.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
