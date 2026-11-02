-- SQLite twin of schema.sql, used ONLY by the automated tests.
CREATE TABLE categories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE COLLATE NOCASE,
    description TEXT NULL,
    created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE profiles (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL UNIQUE COLLATE NOCASE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO profiles (name) VALUES ('Household');
CREATE TABLE expenses (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    title        TEXT NOT NULL,
    amount       NUMERIC NOT NULL CHECK (amount > 0),
    expense_date TEXT NOT NULL,
    category_id  INTEGER NOT NULL REFERENCES categories (id) ON DELETE RESTRICT,
    profile_id   INTEGER NOT NULL DEFAULT 1 REFERENCES profiles (id) ON DELETE RESTRICT,
    notes        TEXT NULL,
    created_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
