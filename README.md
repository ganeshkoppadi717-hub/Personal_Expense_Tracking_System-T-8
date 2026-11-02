# Personal Expense Tracking System

## Deploy the live website on Vercel

The app is configured for Vercel Functions with a Vercel Marketplace Neon
PostgreSQL database. It retains MySQL for local use. Your local database and
its expenses are never uploaded automatically.

1. Import this GitHub repository into Vercel. Set **Root Directory** to `.`.
2. Install Neon from the Vercel Marketplace, choose the **Free** plan, create
   a database, and connect it to the project’s Development, Preview, and
   Production environments. The integration supplies the private `DATABASE_URL`.
3. Add these Vercel environment variables:
   - `DB_BACKEND` = `postgres`
   - `PUBLIC_DEMO` = `true`
   - `SECRET_KEY` = a privately generated random value
   - `CURRENCY_SYMBOL` = `₹` (optional)
4. Run `Personal_Expense_Tracking_System/schema_postgres.sql` in Neon’s SQL
   editor, then redeploy. To seed fictional examples, configure the database
   URL securely in a local shell and run
   `python Personal_Expense_Tracking_System/init_postgres_db.py --sample`.

The target plans are Vercel Hobby and Neon Free ($0 within their usage quotas).
Check plan selection and usage; do not enable paid plans if you require a $0
budget.

**This is a public, unauthenticated demo:** anyone can see, add, edit, or delete
shared entries. It warns visitors not to enter personal financial data. Local
MySQL data is not copied.

For local Windows setup and tests, see
[the application README](./Personal_Expense_Tracking_System/README.md).
