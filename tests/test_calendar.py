
import asyncio
import unittest

from calendars import SimpleCalendar


class TestCalendar(unittest.TestCase):

    def test_calendar_buttons(self):
        """Check the English calendar labels."""
        calendar = asyncio.run(
            SimpleCalendar().start_calendar(2026, 11)
        )

        buttons = [
            button.text
            for row in calendar.inline_keyboard
            for button in row
        ]

        self.assertIn("November 2026", buttons)
        self.assertIn("Mon", buttons)
        self.assertIn("Sun", buttons)
        self.assertIn("14", buttons)

    def test_calendar_navigation(self):
        """Check that navigation buttons exist."""
        calendar = asyncio.run(
            SimpleCalendar().start_calendar(2026, 11)
        )

        callbacks = [
            button.callback_data
            for row in calendar.inline_keyboard
            for button in row
        ]

        self.assertTrue(
            any("NEXT-MONTH" in value for value in callbacks)
        )

        self.assertTrue(
            any("PREV-MONTH" in value for value in callbacks)
        )


if __name__ == "__main__":
    unittest.main()
