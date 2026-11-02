# Personal Expense Tracking System

A beginner-friendly web application to record, filter and analyse personal expenses.
Built with **Python, Flask, MySQL, HTML, CSS, JavaScript, Pandas, NumPy and Matplotlib**.

## Features

- Add, view, edit and delete expenses (amount must be greater than zero)
- Add shared people profiles and assign each expense to a person; filter dashboards, expenses,
  reports, charts and CSV exports by person
- Manage categories (add, rename, delete; a category that still has expenses cannot be deleted)
- Filter by date range, by category, or both together
- Dashboard: total, count, average, highest, this-month total, category totals with percentages,
  interactive category and monthly charts
- Monthly report (total, average, median, standard deviation, category breakdown, top 5 expenses)
- CSV download of the filtered expenses
- Friendly error messages for bad input and for database/configuration problems
- Automated tests and a database diagnostic command

## Project structure

```
Personal_Expense_Tracking_System/
  app.py             Flask application (routes)
  config.py          Settings read from .env
  db.py              Database connection helper (parameterized SQL only)
  repository.py      All SQL queries for profiles, categories and expenses
  validators.py      Input validation
  init_db.py         Creates the database/tables and loads sample data
  diagnose.py        Checks Python packages, .env and the MySQL connection
  schema.sql         MySQL tables (safe to rerun to upgrade)
  sample_data.sql    Fictional sample categories and expenses
  .env.example       Template for your own MySQL settings
  requirements.txt   Python packages
  start_app.bat      Optional Windows launcher
  analysis/          stats.py (Pandas/NumPy), charts.py (Matplotlib), reports.py
  templates/         HTML pages (Jinja2)
  static/            css/style.css, js/app.js
  tests/             Automated tests
  docs/              Project report, presentation and notes
```

## Requirements

- Windows 10/11, **Python 3.10 or newer (64-bit)** - tick "Add python.exe to PATH" when installing
- **MySQL Server 8.0 or newer** (MySQL Installer from mysql.com) - remember the root password you choose
- Visual Studio Code and Google Chrome

## Setup on Windows (PowerShell)

### 1. Download and extract
Download `Personal_Expense_Tracking_System.zip`, right-click it > **Extract All...**
(for example to `C:\Projects`). You get the folder `C:\Projects\Personal_Expense_Tracking_System`.

### 2. Open the folder in Visual Studio Code
Start VS Code > **File > Open Folder...** > choose `Personal_Expense_Tracking_System`.
Open a terminal with **Terminal > New Terminal** (it is PowerShell and already inside the project folder).
**Run every command below from this project folder** (the folder that contains `app.py`).

Check that you are in the right place:
```powershell
dir app.py
```

### 3. Create a virtual environment
```powershell
python -m venv .venv
```

### 4. Activate it
```powershell
.\.venv\Scripts\Activate.ps1
```
If PowerShell says *"running scripts is disabled"*, run this once and try again:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```
You should now see `(.venv)` at the start of the prompt. If VS Code asks which Python interpreter to use, choose the one inside `.venv`.

### 5. Install the dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Make sure MySQL is running
Press **Win + R**, type `services.msc`, find **MySQL80** (or similar) and make sure it is *Running*.

### 7. Enter your MySQL settings
```powershell
Copy-Item .env.example .env
notepad .env
```
Change `DB_PASSWORD` to **your own MySQL root password** (and `DB_USER` if you use another user). Save and close.
The `.env` file stays on your computer only. Never share it.

### 8. Create the database and tables, and load sample data
```powershell
python init_db.py --sample
```
This creates the database `expense_tracker`, the tables, and ~34 fictional expenses.
It also upgrades existing expense tables by assigning older expenses to the default
`Household` profile. The upgrade never deletes existing data, and sample loading is
skipped if expenses already exist.
Use `python init_db.py` (without `--sample`) if you want an empty database.

*Alternative (MySQL Workbench):* for a new database, open `schema.sql` and run it, then open
`sample_data.sql` and run it **once**. Use `python init_db.py` to safely upgrade an existing
database so its current expenses are assigned to a profile.

### 9. Verify the database
```powershell
python diagnose.py
```
You should see `[ OK ]` lines, including `Table 'expenses' exists: 34 row(s)`.
You can also check inside MySQL:
```sql
USE expense_tracker;
SHOW TABLES;
SELECT COUNT(*) FROM expenses;
```

### 10. Start the server
```powershell
python app.py
```
Or double-click `start_app.bat` (it only starts the app; it installs nothing).

### 11. Open the application in Chrome
Go to **http://127.0.0.1:5000**. Stop the server with **Ctrl + C** in the terminal.

### 12. Run the automated tests
Open a second terminal in the project folder, activate the environment (step 4), then:
```powershell
python -m unittest discover -s tests -t . -v
```
The tests use a temporary SQLite file, so your real MySQL data is never changed.

**Optional - tests against a real MySQL test database.** These are skipped unless you set:
```powershell
$env:TEST_DB_USER="root"
$env:TEST_DB_PASSWORD="your MySQL password"
$env:TEST_DB_NAME="expense_tracker_test"
python -m unittest discover -s tests -t . -v
```
The name must end in `_test`; the tests create that separate database and empty it before every test.

## Troubleshooting

| Problem | What to do |
|---|---|
| `python` is not recognised | Reinstall Python and tick "Add python.exe to PATH", then reopen VS Code. |
| `Activate.ps1 cannot be loaded` | Run the `Set-ExecutionPolicy` command in step 4. |
| `ModuleNotFoundError: No module named 'flask'` | The environment is not active or packages are missing: do steps 4 and 5. |
| Page says "database is not ready" | Run `python diagnose.py` and fix the `[FAIL]` lines. |
| `Access denied for user` | Wrong `DB_USER` / `DB_PASSWORD` in `.env`. |
| `Cannot reach the MySQL server` | Start the MySQL service (step 6); check `DB_HOST` and `DB_PORT`. |
| `Unknown database 'expense_tracker'` | Run `python init_db.py`. |
| `Port 5000 is already in use` | Close the other program, or change the port at the bottom of `app.py`. |
| Sample data was skipped | Expenses already exist; that is intended. |
| Changed `.env` but nothing changed | Stop the server (Ctrl+C) and start it again. |

## Vercel deployment with PostgreSQL

The repository root is configured for a Flask deployment on Vercel and the
Vercel Marketplace's Neon PostgreSQL integration. The app can still use MySQL
for local development. The Vercel database is separate from local MySQL; this
setup never uploads or copies local expenses.

### Connect a free database

1. Import this GitHub repository into Vercel with the repository root (`.`) as
   the Root Directory. Vercel detects the Flask app from `app.py` and
   `requirements.txt`.
2. From Vercel Marketplace, install the **Neon** integration. Select its **Free**
   plan and create a database; the current Neon free plan is $0 and requires no
   credit card. Connect it to this Vercel project for Development, Preview and
   Production so it provides `DATABASE_URL`.
3. In the Vercel project's **Settings > Environment Variables**, set:
   - `DB_BACKEND` = `postgres`
   - `PUBLIC_DEMO` = `true`
   - `SECRET_KEY` = a new, long random value generated privately (for example,
     `python -c "import secrets; print(secrets.token_hex(32))"`)
   - `CURRENCY_SYMBOL` = `₹` (optional)
   Keep `DATABASE_URL` private; Neon supplies it through the integration. Never
   paste database URLs or secret values into source code, issues, or chat.
4. In Neon’s SQL editor, run `Personal_Expense_Tracking_System/schema_postgres.sql`.
   To load fictional sample data instead, securely configure the same
   `DATABASE_URL` in a local environment and run
   `python Personal_Expense_Tracking_System/init_postgres_db.py --sample`.
   This seeds only invented demo expenses and is safe to repeat.
5. Redeploy after linking the database and setting environment variables.

Neon's Free plan and Vercel Hobby are $0 within their published quotas. They
have usage limits, and providers may change plans or terms; check that each
resource remains on its free plan and monitor usage. Do not select a paid plan
if you need a strict $0 budget.

**Public demo warning:** with `PUBLIC_DEMO=true` the app is intentionally
unauthenticated. Anyone can view, add, edit and delete the shared data. The
site displays a warning and should contain fictional data only; never enter
personal financial information. Existing local MySQL data is not migrated.

## Security notes

- All SQL uses parameterized queries; HTML output is escaped; forms use CSRF tokens.
- No passwords are stored in the project. `.env` is listed in `.gitignore`.
- The server binds to `127.0.0.1` (only your own computer can open it). It is a demo/learning setup, not a production deployment.
