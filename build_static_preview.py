"""Build the read-only, fictional-data website preview for Vercel."""
import calendar
import re
import shutil
import sqlite3
import sys
import tempfile
from datetime import date
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parent
APP_DIR = ROOT / "Personal_Expense_Tracking_System"
OUTPUT_DIR = ROOT / "public"
PAGES = {
    "/": "index.html",
    "/expenses": "expenses/index.html",
    "/expenses/add": "expenses/add/index.html",
    "/categories": "categories/index.html",
    "/people": "people/index.html",
    "/reports": "reports/index.html",
}

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


def _seed_preview_data(repo):
    profile_ids = {
        "Alex": repo.create_profile("Alex"),
        "Jordan": repo.create_profile("Jordan"),
    }
    categories = {
        name: repo.create_category(name, description)
        for name, description in (
            ("Groceries", "Everyday groceries and household essentials"),
            ("Dining", "Coffee, meals and dining out"),
            ("Transport", "Public transport and travel"),
            ("Utilities", "Home utilities and subscriptions"),
            ("Wellness", "Health and personal care"),
        )
    }
    today = date.today()
    samples = (
        ("Weekly groceries", "84.60", "Groceries", "Alex", "Market and pantry staples"),
        ("Coffee with friends", "16.80", "Dining", "Jordan", "Weekend catch-up"),
        ("Monthly transit pass", "42.00", "Transport", "Alex", "Local travel"),
        ("Home internet", "58.00", "Utilities", "Jordan", "Monthly service"),
        ("Pharmacy essentials", "23.40", "Wellness", "Alex", "Personal care"),
        ("Dinner out", "49.50", "Dining", "Jordan", ""),
    )
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
            repo.create_expense({
                "title": title,
                "amount": Decimal(amount),
                "expense_date": date(year, month, day),
                "category_id": categories[category],
                "profile_id": profile_ids[profile],
                "notes": notes,
            })


def _make_static_preview(html):
    html = html.replace(
        '<main class="container">',
        '<main class="container">\n'
        '<aside class="flash warning" role="status"><span><strong>Static preview</strong> '
        '— This site uses fictional sample data. Changes, filters and exports are disabled '
        'and nothing is saved.</span></aside>',
        1,
    )
    html = re.sub(
        r"<form\b([^>]*)>",
        lambda match: "<form" + match.group(1)
        + ' data-static-preview="true" onsubmit="return false;">',
        html,
        flags=re.IGNORECASE,
    )
    html = re.sub(
        r"<(input|select|textarea|button)\b([^>]*)>",
        lambda match: "<" + match.group(1) + match.group(2)
        + ("" if re.search(r"\bdisabled(?:\s|=|$)", match.group(2), re.IGNORECASE)
           else " disabled")
        + ">",
        html,
        flags=re.IGNORECASE,
    )
    html = re.sub(
        r'<a\b([^>]*\bhref="/export\.csv(?:\?[^"]*)?"[^>]*)>(.*?)</a>',
        lambda match: "<span"
        + re.sub(r'\s+href="[^"]*"', "", match.group(1), flags=re.IGNORECASE)
        + ' aria-disabled="true">'
        + match.group(2)
        + "</span>",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    html = re.sub(
        r'<a\b([^>]*\bhref="/expenses/\d+/edit"[^>]*)>(.*?)</a>',
        lambda match: "<span"
        + re.sub(r'\s+href="[^"]*"', "", match.group(1), flags=re.IGNORECASE)
        + ' aria-disabled="true">'
        + match.group(2)
        + "</span>",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return html


def build(output_dir=OUTPUT_DIR):
    from app import create_app

    output_dir = Path(output_dir)
    with tempfile.TemporaryDirectory(prefix="expense-static-preview-") as temp_dir:
        db_path = Path(temp_dir) / "preview.sqlite3"
        connection = sqlite3.connect(str(db_path))
        try:
            schema = (APP_DIR / "tests" / "sqlite_schema.sql").read_text(encoding="utf-8")
            connection.executescript(schema)
            connection.commit()
        finally:
            connection.close()

        app = create_app({
            "DB_BACKEND": "sqlite",
            "SQLITE_PATH": str(db_path),
            "SECRET_KEY": "static-preview-build-only",
            "TESTING": True,
            "CSRF_ENABLED": False,
            "CURRENCY_SYMBOL": "₹",
            "STATIC_PREVIEW": True,
        })
        _seed_preview_data(app.extensions["expense_repo"])

        output_dir.mkdir(parents=True, exist_ok=True)
        with app.test_client() as client:
            for route, relative_path in PAGES.items():
                response = client.get(route)
                if response.status_code != 200:
                    raise RuntimeError(
                        "Could not render static preview route %s (HTTP %s)."
                        % (route, response.status_code)
                    )
                target = output_dir / relative_path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(
                    _make_static_preview(response.get_data(as_text=True)),
                    encoding="utf-8",
                )

    shutil.copytree(APP_DIR / "static", output_dir / "static", dirs_exist_ok=True)
    print("Built six read-only static preview pages in %s" % output_dir)


if __name__ == "__main__":
    build()
