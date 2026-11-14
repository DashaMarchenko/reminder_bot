
import asyncio
import unittest
from unittest.mock import patch

from app.main import bot_main
from bot_config import bot, dp


class TestHandlers(unittest.TestCase):

    def test_handler_registration(self):
        """Check that Telegram handlers are registered."""

        with patch.object(bot, "set_my_commands") as mock:
            async def fake_set_commands(*args, **kwargs):
                return True

            mock.side_effect = fake_set_commands

            asyncio.run(bot_main())

        self.assertGreater(
            len(dp.message_handlers.handlers),
            0
        )

        self.assertGreater(
            len(dp.callback_query_handlers.handlers),
            0
        )


if __name__ == "__main__":
    unittest.main()
