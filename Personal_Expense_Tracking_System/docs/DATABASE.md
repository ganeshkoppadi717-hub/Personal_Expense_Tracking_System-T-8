# Database design

MySQL database `expense_tracker`, three tables (InnoDB, utf8mb4).

**profiles**: `id` (PK, auto increment), `name` (VARCHAR 50, unique, not null), `created_at`.

**categories**: `id` (PK, auto increment), `name` (VARCHAR 50, unique, not null), `description` (VARCHAR 255, null), `created_at`.

**expenses**: `id` (PK), `title` (VARCHAR 100), `amount` (DECIMAL(10,2), CHECK amount > 0), `expense_date` (DATE), `category_id` (FK -> categories.id, ON DELETE RESTRICT), `profile_id` (FK -> profiles.id, ON DELETE RESTRICT), `notes` (VARCHAR 500, null), `created_at`. Indexes on `expense_date`, `category_id` and `profile_id`.

Relationships: one category and one profile can each have many expenses. People are shared profiles, not login accounts. Existing expenses are assigned to the first profile (the initial `Household` profile) when `python init_db.py` upgrades an existing database. Profiles are retained so expense history cannot be orphaned.

Rules enforced twice (in the web application and in the database): positive amount, required fields, valid category and valid profile.
