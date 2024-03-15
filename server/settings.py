import os
from pathlib import Path

from sqlmodel import create_engine

BASE_DIR = Path(__file__).resolve().parent
SQLITE_FILENAME = os.getenv('SQLITE_DATABASE', 'db.sqlite3')

ENGINE = create_engine(
    'sqlite:///%s' % (BASE_DIR.parent / SQLITE_FILENAME),
    echo=True,
)
