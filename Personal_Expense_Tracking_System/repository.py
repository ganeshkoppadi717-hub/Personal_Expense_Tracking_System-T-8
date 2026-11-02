"""All database reads/writes for categories and expenses (parameterized SQL)."""
from datetime import date, datetime
from decimal import Decimal


class CategoryInUse(Exception):
    """Raised when deleting a category that still has expenses."""


def _to_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def _to_money(value):
    return Decimal(str(value)).quantize(Decimal("0.01"))


def _iso(value):
    return value.isoformat() if isinstance(value, date) else str(value)


def _where(filters, backend="mysql"):
    filters = filters or {}
    clauses, params = [], []
    if filters.get("start"):
        clauses.append("e.expense_date >= %s")
        params.append(_date_param(filters["start"], backend))
    if filters.get("end"):
        clauses.append("e.expense_date <= %s")
        params.append(_date_param(filters["end"], backend))
    if filters.get("category_id"):
        clauses.append("e.category_id = %s")
        params.append(int(filters["category_id"]))
    if filters.get("profile_id"):
        clauses.append("e.profile_id = %s")
        params.append(int(filters["profile_id"]))
    sql = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    return sql, params


def _date_param(value, backend):
    if backend == "postgres":
        return date.fromisoformat(str(value)[:10])
    return _iso(value)


class Repository:
    def __init__(self, db):
        self.db = db

    # ---- categories ------------------------------------------------------
    def list_profiles(self):
        return self.db.query_all(
            "SELECT p.id, p.name, COUNT(e.id) AS expense_count "
            "FROM profiles p LEFT JOIN expenses e ON e.profile_id = p.id "
            "GROUP BY p.id, p.name ORDER BY p.name")

    def get_profile(self, profile_id):
        return self.db.query_one(
            "SELECT id, name FROM profiles WHERE id = %s", (profile_id,))

    def profile_name_taken(self, name):
        return self.db.query_one(
            "SELECT id FROM profiles WHERE LOWER(name) = LOWER(%s)", (name,)) is not None

    def create_profile(self, name):
        new_id, _ = self.db.execute(
            "INSERT INTO profiles (name) VALUES (%s)", (name,))
        return new_id

    def list_categories(self):
        return self.db.query_all(
            "SELECT c.id, c.name, c.description, COUNT(e.id) AS expense_count "
            "FROM categories c LEFT JOIN expenses e ON e.category_id = c.id "
            "GROUP BY c.id, c.name, c.description ORDER BY c.name")

    def get_category(self, category_id):
        return self.db.query_one(
            "SELECT id, name, description FROM categories WHERE id = %s", (category_id,))

    def category_name_taken(self, name, exclude_id=None):
        if exclude_id is None:
            row = self.db.query_one(
                "SELECT id FROM categories WHERE LOWER(name) = LOWER(%s)", (name,))
        else:
            row = self.db.query_one(
                "SELECT id FROM categories WHERE LOWER(name) = LOWER(%s) AND id <> %s",
                (name, exclude_id))
        return row is not None

    def create_category(self, name, description):
        new_id, _ = self.db.execute(
            "INSERT INTO categories (name, description) VALUES (%s, %s)", (name, description))
        return new_id

    def update_category(self, category_id, name, description):
        _, count = self.db.execute(
            "UPDATE categories SET name = %s, description = %s WHERE id = %s",
            (name, description, category_id))
        return count

    def delete_category(self, category_id):
        row = self.db.query_one(
            "SELECT COUNT(*) AS n FROM expenses WHERE category_id = %s", (category_id,))
        if int(row["n"]) > 0:
            raise CategoryInUse()
        _, count = self.db.execute("DELETE FROM categories WHERE id = %s", (category_id,))
        return count

    # ---- expenses --------------------------------------------------------
    @staticmethod
    def _clean_row(row):
        row["amount"] = _to_money(row["amount"])
        row["expense_date"] = _to_date(row["expense_date"])
        return row

    _SELECT = (
        "SELECT e.id, e.title, e.amount, e.expense_date, e.category_id, "
        "e.profile_id, p.name AS profile_name, c.name AS category_name, e.notes "
        "FROM expenses e INNER JOIN categories c ON c.id = e.category_id "
        "INNER JOIN profiles p ON p.id = e.profile_id")

    def list_expenses(self, filters=None):
        where, params = _where(filters, self.db.backend)
        rows = self.db.query_all(
            self._SELECT + where + " ORDER BY e.expense_date DESC, e.id DESC", params)
        return [self._clean_row(r) for r in rows]

    def get_expense(self, expense_id):
        row = self.db.query_one(self._SELECT + " WHERE e.id = %s", (expense_id,))
        return self._clean_row(row) if row else None

    def create_expense(self, data):
        new_id, _ = self.db.execute(
            "INSERT INTO expenses (title, amount, expense_date, category_id, profile_id, notes) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (data["title"], str(data["amount"]),
             _date_param(data["expense_date"], self.db.backend),
             data["category_id"], data["profile_id"], data["notes"]))
        return new_id

    def update_expense(self, expense_id, data):
        _, count = self.db.execute(
            "UPDATE expenses SET title = %s, amount = %s, expense_date = %s, "
            "category_id = %s, profile_id = %s, notes = %s WHERE id = %s",
            (data["title"], str(data["amount"]),
             _date_param(data["expense_date"], self.db.backend),
             data["category_id"], data["profile_id"], data["notes"], expense_id))
        return count

    def delete_expense(self, expense_id):
        _, count = self.db.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
        return count

    def total_amount(self, filters=None):
        """SQL SUM of the filtered expenses (used to cross-check the dashboard)."""
        where, params = _where(filters, self.db.backend)
        row = self.db.query_one(
            "SELECT COALESCE(SUM(e.amount), 0) AS total FROM expenses e" + where, params)
        return _to_money(row["total"])
