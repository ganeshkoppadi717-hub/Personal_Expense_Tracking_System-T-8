# Database design

Local development uses the MySQL database `expense_tracker` (InnoDB, utf8mb4).
The Vercel deployment can use PostgreSQL/Neon with the parallel schema in
`schema_postgres.sql`; set `DB_BACKEND=postgres` and configure `DATABASE_URL`.
Run `python init_postgres_db.py --sample` to create the PostgreSQL schema and
seed fictional sample data. This does not read or migrate the local MySQL data.

Both backends use the same three tables:

**profiles**: `id` (PK, auto increment), `name` (VARCHAR 50, unique, not null), `created_at`.

**categories**: `id` (PK, auto increment), `name` (VARCHAR 50, unique, not null), `description` (VARCHAR 255, null), `created_at`.

**expenses**: `id` (PK), `title` (VARCHAR 100), `amount` (DECIMAL(10,2), CHECK amount > 0), `expense_date` (DATE), `category_id` (FK -> categories.id, ON DELETE RESTRICT), `profile_id` (FK -> profiles.id, ON DELETE RESTRICT), `notes` (VARCHAR 500, null), `created_at`. Indexes on `expense_date`, `category_id` and `profile_id`.

Relationships: one category and one profile can each have many expenses. People are shared profiles, not login accounts. Existing expenses are assigned to the first profile (the initial `Household` profile) when `python init_db.py` upgrades an existing database. Profiles are retained so expense history cannot be orphaned.

Rules enforced twice (in the web application and in the database): positive amount, required fields, valid category and valid profile.

The Vercel demo is intentionally public and unauthenticated when
`PUBLIC_DEMO=true`. Anyone can change or delete shared rows. Use fictional data
only; do not connect or copy personal expense records to this public demo.
