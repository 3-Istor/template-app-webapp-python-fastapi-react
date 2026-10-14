import sqlite3
from pathlib import Path

from alembic import command
from alembic.config import Config

from app.config import get_settings

BACKEND_DIR = Path(__file__).resolve().parent.parent


def upgrade_to_head(db_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("DB_TYPE", "sqlite")
    monkeypatch.setenv("SQLITE_PATH", str(db_path))
    get_settings.cache_clear()
    try:
        command.upgrade(Config(str(BACKEND_DIR / "alembic.ini")), "head")
    finally:
        get_settings.cache_clear()


def applied_revision(db_path: Path) -> str:
    with sqlite3.connect(db_path) as connection:
        return connection.execute("SELECT version_num FROM alembic_version").fetchone()[0]


def test_migrations_reach_head_on_an_empty_database(tmp_path, monkeypatch):
    db_path = tmp_path / "app.db"

    upgrade_to_head(db_path, monkeypatch)

    assert applied_revision(db_path) == "0001"


def test_migrations_are_idempotent_when_rerun(tmp_path, monkeypatch):
    db_path = tmp_path / "app.db"
    upgrade_to_head(db_path, monkeypatch)

    upgrade_to_head(db_path, monkeypatch)

    assert applied_revision(db_path) == "0001"
