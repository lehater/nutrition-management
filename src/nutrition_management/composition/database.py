from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine, event


def create_sqlite_engine(path: str | Path):
    # Python's sqlite3 legacy transaction control does not start a transaction for SELECT.
    # autocommit=False opts into modern PEP-249 transaction behavior so an explicit
    # SQLAlchemy read transaction establishes one WAL snapshot on its first statement.
    engine = create_engine(
        f"sqlite:///{Path(path)}",
        future=True,
        connect_args={"autocommit": False},
    )

    @event.listens_for(engine, "connect")
    def _sqlite_pragmas(dbapi_connection, _connection_record):
        # sqlite3 requires autocommit while changing connection-wide PRAGMAs such as
        # foreign_keys. Restore the configured transaction mode afterwards.
        previous_autocommit = dbapi_connection.autocommit
        dbapi_connection.autocommit = True
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=FULL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA read_uncommitted=OFF")
            cursor.close()
        finally:
            dbapi_connection.autocommit = previous_autocommit

    return engine
