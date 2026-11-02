import unittest
from datetime import date

from init_postgres_db import seed_sample
from repository import _where
from tests.base import AppTestCase


class PostgresQueryTests(unittest.TestCase):
    def test_date_filters_use_postgres_date_parameters(self):
        _, params = _where({
            "start": "2026-10-01",
            "end": "2026-10-31",
        }, "postgres")
        self.assertEqual(params, [date(2026, 10, 1), date(2026, 10, 31)])


class PostgresSetupTests(AppTestCase):
    def test_demo_seed_is_fictional_and_idempotent(self):
        seed_sample(self.repo)
        first_run = self.repo.list_expenses()
        self.assertGreater(len(first_run), 0)
        self.assertEqual(
            {row["profile_name"] for row in first_run},
            {"Alex", "Jordan"},
        )
        self.assertTrue(
            {row["category_name"] for row in first_run}
            <= {"Groceries", "Dining", "Transport", "Utilities", "Wellness"}
        )
        self.assertGreaterEqual(
            len(self.repo.list_categories()),
            5,
        )

        seed_sample(self.repo)
        self.assertEqual(len(self.repo.list_expenses()), len(first_run))


if __name__ == "__main__":
    unittest.main()
