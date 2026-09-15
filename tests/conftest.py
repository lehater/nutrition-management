from alembic import command
from alembic.config import Config
import pytest

from nutrition_management.composition.database import create_sqlite_engine


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "nutrition-management-test.db"


@pytest.fixture
def engine(db_path):
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(config, "head")
    engine = create_sqlite_engine(db_path)
    try:
        yield engine
    finally:
        engine.dispose()
