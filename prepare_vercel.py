"""Copy application assets to Vercel's static public directory."""
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "Personal_Expense_Tracking_System" / "static"
DESTINATION = ROOT / "public" / "static"


if __name__ == "__main__":
    shutil.copytree(SOURCE, DESTINATION, dirs_exist_ok=True)
    print("Copied static assets to %s" % DESTINATION)
