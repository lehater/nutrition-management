from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from nutrition_management.composition.database import create_sqlite_engine


def test_mvp_v1_migrations_extend_pr7_schema_with_open_bounds_and_safety_mapping(tmp_path):
    db_path = tmp_path / "mvp-v1-migrations.db"
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(config, "0001")
    command.upgrade(config, "head")

    engine = create_sqlite_engine(db_path)
    try:
        inspector = inspect(engine)
        tables = set(inspector.get_table_names())
        assert {"nt_reference_mapping", "nt_safety_mapping"} <= tables
        reference_columns = {item["name"] for item in inspector.get_columns("nt_standard_reference")}
        assert {"lower_inclusive", "upper_inclusive"} <= reference_columns
    finally:
        engine.dispose()
