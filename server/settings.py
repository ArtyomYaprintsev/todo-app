import os
from pathlib import Path

from sqlmodel import create_engine

BASE_DIR = Path(__file__).resolve().parent

DB_URL = os.getenv("DB_URL", "sqlite:///db.sqlite3")

ENGINE = create_engine(DB_URL, echo=True)
