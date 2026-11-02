"""Initialize a PostgreSQL/Neon database without touching local MySQL data.

Run with DB_BACKEND=postgres and DATABASE_URL configured:
    python init_postgres_db.py --sample
"""
import argparse
import calendar
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

from config import config_as_dict
from db import Database, DatabaseError, config_problems
from repository import Repository


BASE_DIR = Path(__file__).resolve().parent


def _statements(sql_text):
    lines = [line for line in sql_text.splitlines()
             if not line.strip().startswith("--")]
    return [statement.strip() for statement in "\n".join(lines).split(";")
            if statement.strip()]


def create_schema(db):
    schema = (BASE_DIR / "schema_postgres.sql").read_text(encoding="utf-8")
    with db.connection() as conn:
        try:
            with conn.cursor() as cursor:
                for statement in _statements(schema):
                    cursor.execute(statement)
            conn.commit()
        except Exception:
            conn.rollback()
            raise


def seed_sample(repo):
    profiles = {profile["name"]: profile["id"] for profile in repo.list_profiles()}
    for name in ("Alex", "Jordan"):
        if name not in profiles:
            profiles[name] = repo.create_profile(name)

    categories = {
        category["name"]: category["id"] for category in repo.list_categories()
    }
    for name, description in (
        ("Groceries", "Everyday groceries and household essentials"),
        ("Dining", "Coffee, meals and dining out"),
        ("Transport", "Public transport and travel"),
        ("Utilities", "Home utilities and subscriptions"),
        ("Wellness", "Health and personal care"),
    ):
        if name not in categories:
            categories[name] = repo.create_category(name, description)

    samples = (
        ("Weekly groceries", "84.60", "Groceries", "Alex", "Market and pantry staples"),
        ("Coffee with friends", "16.80", "Dining", "Jordan", "Weekend catch-up"),
        ("Monthly transit pass", "42.00", "Transport", "Alex", "Local travel"),
        ("Home internet", "58.00", "Utilities", "Jordan", "Monthly service"),
        ("Pharmacy essentials", "23.40", "Wellness", "Alex", "Personal care"),
        ("Dinner out", "49.50", "Dining", "Jordan", ""),
    )
    today = date.today()
    for month_offset in range(11, -1, -1):
        year = today.year
        month = today.month - month_offset
        while month <= 0:
            year -= 1
            month += 12
        last_day = calendar.monthrange(year, month)[1]
        for index, sample in enumerate(samples[:2 + (month % 3 == 0)]):
            title, amount, category, profile, notes = sample
            day = min((5, 16, 23)[index], last_day)
            if year == today.year and month == today.month:
                day = min(day, today.day)
            expense_date = date(year, month, day)
            exists = repo.db.query_one(
                "SELECT id FROM expenses WHERE title = %s AND expense_date = %s "
                "AND profile_id = %s",
                (title, expense_date, profiles[profile]),
            )
            if exists is None:
                repo.create_expense({
                    "title": title,
                    "amount": Decimal(amount),
                    "expense_date": expense_date,
                    "category_id": categories[category],
                    "profile_id": profiles[profile],
                    "notes": notes,
                })


def main(argv=None):
    parser = argparse.ArgumentParser(description="Initialize a PostgreSQL expense database.")
    parser.add_argument("--sample", action="store_true",
                        help="add fictional demo data (safe to repeat)")
    args = parser.parse_args(argv)

    cfg = config_as_dict()
    if cfg.get("DB_BACKEND") != "postgres":
        print("Set DB_BACKEND=postgres before initializing this database.")
        return 1
    problems = config_problems(cfg)
    if problems:
        print("Cannot continue:")
        for problem in problems:
            print("  -", problem)
        return 1

    db = Database(cfg)
    try:
        create_schema(db)
        if args.sample:
            seed_sample(Repository(db))
    except DatabaseError as exc:
        print("Could not initialize PostgreSQL:", exc)
        return 1
    except Exception as exc:
        sqlstate = getattr(exc, "sqlstate", None)
        detail = "SQLSTATE %s" % sqlstate if sqlstate else type(exc).__name__
        print("Could not initialize PostgreSQL (%s). Check the schema and database logs."
              % detail)
        return 1

    print("PostgreSQL schema is ready.")
    if args.sample:
        print("Fictional demo data is ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
