
import unittest
from datetime import datetime, timezone

from handlers.reminder import localize_time


class TestTimezones(unittest.TestCase):

    def test_vienna_winter(self):
        """Vienna uses UTC+1 in winter."""
        local = localize_time(
            datetime(2026, 12, 25, 14, 30),
            "Europe/Vienna"
        )

        utc = local.astimezone(timezone.utc)

        self.assertEqual((utc.hour, utc.minute), (13, 30))

    def test_vienna_summer(self):
        """Vienna uses UTC+2 in summer."""
        local = localize_time(
            datetime(2027, 7, 15, 14, 30),
            "Europe/Vienna"
        )

        utc = local.astimezone(timezone.utc)

        self.assertEqual((utc.hour, utc.minute), (12, 30))

    def test_bangkok(self):
        """Bangkok uses UTC+7."""
        local = localize_time(
            datetime(2027, 7, 15, 14, 30),
            "Asia/Bangkok"
        )

        utc = local.astimezone(timezone.utc)

        self.assertEqual((utc.hour, utc.minute), (7, 30))

    def test_new_york(self):
        """New York uses UTC-4 in July."""
        local = localize_time(
            datetime(2027, 7, 15, 14, 30),
            "America/New_York"
        )

        utc = local.astimezone(timezone.utc)

        self.assertEqual((utc.hour, utc.minute), (18, 30))

    def test_nonexistent_time(self):
        """Reject a time skipped during the DST transition."""
        with self.assertRaises(ValueError):
            localize_time(
                datetime(2027, 3, 28, 2, 30),
                "Europe/Vienna"
            )

    def test_ambiguous_time(self):
        """Reject a time occurring twice during the DST transition."""
        with self.assertRaises(ValueError):
            localize_time(
                datetime(2027, 10, 31, 2, 30),
                "Europe/Vienna"
            )


if __name__ == "__main__":
    unittest.main()
