
import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple
from contextlib import contextmanager, closing

from config import load_config


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "users.db"
LOG_PATH = BASE_DIR / "logs" / "bot_db_log.log"
CONFIG_PATH = BASE_DIR / "config" / "config.ini"

config = load_config(str(CONFIG_PATH))


class Remind(NamedTuple):
    id: str
    user_id: int
    name: str
    text: str


class SQLiteDB:
    def __init__(self):
        self.db_path = DB_PATH
        self.logger = self._setup_logger()
        self._create_table_users()
        self._create_table_settings()

    @staticmethod
    def _setup_logger():
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger("bot_db_log")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(levelname)s - %(message)s"
                )
            )
            logger.addHandler(handler)

        return logger

    @contextmanager
    def _connect(self):
        with closing(sqlite3.connect(self.db_path, timeout=10)) as connection:
            with connection:
                yield connection

    def _create_table_users(self):
        """Create the reminders table if it does not exist."""
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    user_id INTEGER,
                    name TEXT,
                    date TEXT,
                    text TEXT
                )
                """
            )

        self.logger.info("Reminders table initialized")


    def _create_table_settings(self):
        """Create a table for user preferences."""
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS user_settings (
                    user_id INTEGER PRIMARY KEY,
                    timezone TEXT NOT NULL DEFAULT 'Europe/Vienna'
                )
                """
            )


    def set_user_timezone(self, user_id: int, timezone_name: str):
        """Save or update a user's timezone."""
        from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

        try:
            ZoneInfo(timezone_name)
        except (ZoneInfoNotFoundError, TypeError, ValueError):
            return False

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO user_settings (user_id, timezone)
                VALUES (?, ?)
                ON CONFLICT(user_id)
                DO UPDATE SET timezone = excluded.timezone
                """,
                (user_id, timezone_name)
            )

        return True


    def get_user_timezone(self, user_id: int):
        """Retrieve a user's timezone."""
        with self._connect() as connection:
            result = connection.execute(
                """
                SELECT timezone
                FROM user_settings
                WHERE user_id = ?
                """,
                (user_id,)
            ).fetchone()

        return result[0] if result else "Europe/Vienna"


    def insert_one_value(
        self,
        user_id: int,
        name: str,
        date: str,
        text: str,
        _id=None
    ):
        """Insert a reminder into the database."""
        reminder_id = _id if _id is not None else str(uuid.uuid4())
        values = (reminder_id, user_id, name, date, text)

        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO users (id, user_id, name, date, text)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    values
                )

            self.logger.info("Reminder %s created", reminder_id)
            return True, 200, values

        except sqlite3.IntegrityError:
            self.logger.warning("Reminder ID already exists: %s", reminder_id)
            return False, 409, "Reminder ID already exists"

        except sqlite3.Error:
            self.logger.exception("Failed to create reminder")
            return False, 500, "Database error"

    def get_all_values_json(self):
        """Return all reminders as a dictionary."""
        try:
            with self._connect() as connection:
                rows = connection.execute(
                    "SELECT id, user_id, name, date, text FROM users"
                ).fetchall()

            return self._get_formatted_json(rows), 200

        except sqlite3.Error:
            self.logger.exception("Failed to retrieve reminders")
            return "Database error", 500

    @staticmethod
    def _get_formatted_json(rows):
        """Convert reminder records to a dictionary."""
        return {
            reminder_id: {
                "user_id": user_id,
                "name": name,
                "date": date,
                "text": text
            }
            for reminder_id, user_id, name, date, text in rows
        }

    def delete_all_values(self):
        """Delete all reminders."""
        try:
            with self._connect() as connection:
                connection.execute("DELETE FROM users")

            self.logger.info("All reminders deleted")
            return "All reminders deleted", 200

        except sqlite3.Error:
            self.logger.exception("Failed to delete reminders")
            return "Database error", 500


    def send_remind(self):
        """Retrieve all due reminders using UTC timestamps."""
        now = datetime.now(timezone.utc).isoformat()

        try:
            with self._connect() as connection:
                rows = connection.execute(
                    """
                    SELECT id, user_id, name, text
                    FROM users
                    WHERE date <= ?
                    ORDER BY date ASC
                    """,
                    (now,)
                ).fetchall()

            return [Remind(*row) for row in rows]

        except sqlite3.Error:
            self.logger.exception("Failed to retrieve due reminders")
            return []


    def delete_reminder(self, reminder_id: str):
        """Delete a reminder after successful delivery."""
        try:
            with self._connect() as connection:
                connection.execute(
                    "DELETE FROM users WHERE id = ?",
                    (reminder_id,)
                )

            self.logger.info("Reminder %s deleted", reminder_id)
            return True

        except sqlite3.Error:
            self.logger.exception("Failed to delete reminder")
            return False
