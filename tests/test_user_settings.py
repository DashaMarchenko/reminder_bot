
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import database.sqlite_db as db_module


class TestUserSettings(unittest.TestCase):

    def test_timezone_settings(self):
        """Test default, insert, update and invalid timezones."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir) / "test.db"

            with patch.object(db_module, "DB_PATH", test_path):
                db = db_module.SQLiteDB()

                self.assertEqual(
                    db.get_user_timezone(123),
                    "Europe/Vienna"
                )

                self.assertTrue(
                    db.set_user_timezone(123, "Asia/Bangkok")
                )

                self.assertEqual(
                    db.get_user_timezone(123),
                    "Asia/Bangkok"
                )

                self.assertTrue(
                    db.set_user_timezone(123, "America/New_York")
                )

                self.assertEqual(
                    db.get_user_timezone(123),
                    "America/New_York"
                )

                self.assertFalse(
                    db.set_user_timezone(123, "Invalid/Timezone")
                )

                self.assertEqual(
                    db.get_user_timezone(123),
                    "America/New_York"
                )


if __name__ == "__main__":
    unittest.main()
