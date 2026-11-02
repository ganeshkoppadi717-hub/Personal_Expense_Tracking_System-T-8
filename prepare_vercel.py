"""Copy application assets to Vercel's static public directory."""
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / "public"
SOURCE = ROOT / "Personal_Expense_Tracking_System" / "static"
DESTINATION = PUBLIC / "static"

STALE_PREVIEW_PATHS = (
    PUBLIC / "index.html",
    PUBLIC / "categories",
    PUBLIC / "expenses",
    PUBLIC / "people",
    PUBLIC / "reports",
)


if __name__ == "__main__":
    for path in STALE_PREVIEW_PATHS:
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink(missing_ok=True)

    shutil.copytree(SOURCE, DESTINATION, dirs_exist_ok=True)
    print("Copied static assets to %s" % DESTINATION)
