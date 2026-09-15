from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine, event


def create_sqlite_engine(path: str | Path):
    engine = create_engine(f"sqlite:///{Path(path)}", future=True)

    @event.listens_for(engine, "connect")
    def _sqlite_pragmas(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=FULL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA read_uncommitted=OFF")
        cursor.close()

    return engine
