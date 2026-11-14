
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import database.sqlite_db as db_module


class TestDatabase(unittest.TestCase):

    def test_insert_select_delete(self):
        """Test creating, retrieving, and deleting a reminder."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir) / "test.db"

            with patch.object(db_module, "DB_PATH", test_path):
                db = db_module.SQLiteDB()

                reminder_date = datetime(
                    2026, 12, 25, 13, 30,
                    tzinfo=timezone.utc
                ).isoformat()

                # INSERT
                result = db.insert_one_value(
                    user_id=123,
                    name="Alice",
                    date=reminder_date,
                    text="Buy Christmas presents"
                )

                self.assertTrue(result[0])
                self.assertEqual(result[1], 200)

                # SELECT
                reminders, status = db.get_all_values_json()

                self.assertEqual(status, 200)
                self.assertEqual(len(reminders), 1)

                reminder = next(iter(reminders.values()))
                self.assertEqual(
                    reminder["text"],
                    "Buy Christmas presents"
                )
                self.assertEqual(
                    reminder["date"],
                    reminder_date
                )

                # DELETE
                reminder_id = result[2][0]

                self.assertTrue(db.delete_reminder(reminder_id))

                reminders, status = db.get_all_values_json()

                self.assertEqual(status, 200)
                self.assertEqual(len(reminders), 0)

    def test_overdue_reminders(self):
        """Test that only due reminders are selected."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir) / "test.db"

            with patch.object(db_module, "DB_PATH", test_path):
                db = db_module.SQLiteDB()

                now = datetime.now(timezone.utc)

                past_date = (
                    now - timedelta(days=1)
                ).isoformat()

                future_date = (
                    now + timedelta(days=1)
                ).isoformat()

                # Insert an overdue reminder.
                db.insert_one_value(
                    123, "Alice", past_date, "Overdue reminder"
                )

                # Insert a future reminder.
                db.insert_one_value(
                    123, "Alice", future_date, "Future reminder"
                )

                reminders = db.send_remind()

                self.assertEqual(len(reminders), 1)
                self.assertEqual(
                    reminders[0].text,
                    "Overdue reminder"
                )


if __name__ == "__main__":
    unittest.main()
