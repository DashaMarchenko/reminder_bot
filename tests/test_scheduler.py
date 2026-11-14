
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from schedule import send_reminder


class TestScheduler(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.reminder = SimpleNamespace(
            id="test-123",
            user_id=12345,
            name="Alice",
            text="Study Python"
        )

    @patch("schedule.DB.delete_reminder")
    @patch("schedule.bot.send_message", new_callable=AsyncMock)
    @patch("schedule.DB.send_remind")
    async def test_successful_delivery(
        self, mock_get, mock_send, mock_delete
    ):
        """Delete a reminder after successful delivery."""
        mock_get.return_value = [self.reminder]

        await send_reminder()

        mock_send.assert_awaited_once_with(
            12345,
            "Alice, here's your reminder:\n\nStudy Python"
        )
        mock_delete.assert_called_once_with("test-123")

    @patch("schedule.DB.delete_reminder")
    @patch("schedule.bot.send_message", new_callable=AsyncMock)
    @patch("schedule.DB.send_remind")
    async def test_failed_delivery(
        self, mock_get, mock_send, mock_delete
    ):
        """Keep the reminder if delivery fails."""
        mock_get.return_value = [self.reminder]
        mock_send.side_effect = RuntimeError("Telegram unavailable")

        await send_reminder()

        mock_delete.assert_not_called()


if __name__ == "__main__":
    unittest.main()
