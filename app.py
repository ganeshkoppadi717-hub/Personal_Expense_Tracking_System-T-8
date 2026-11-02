"""Vercel entry point for the Flask application."""
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent / "Personal_Expense_Tracking_System"
sys.path.insert(0, str(PROJECT_DIR))

from Personal_Expense_Tracking_System.app import create_app


app = create_app()
