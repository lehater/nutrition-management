from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from nutrition_management.composition.database import create_sqlite_engine


def test_bls_v4_migration_extends_current_food_knowledge_schema(tmp_path):
    db_path = tmp_path / "bls-v4-migrations.db"
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(config, "0004")
    command.upgrade(config, "head")

    engine = create_sqlite_engine(db_path)
    try:
        inspector = inspect(engine)
        tables = set(inspector.get_table_names())
        assert {"fk_source_dataset", "fk_component"} <= tables

        food_columns = {item["name"] for item in inspector.get_columns("fk_base_food")}
        assert {"source_id", "source_code", "name_en"} <= food_columns

        nutrient_columns = {item["name"] for item in inspector.get_columns("fk_nutrient_value")}
        assert {"source_value_text", "value_origin", "source_reference"} <= nutrient_columns
    finally:
        engine.dispose()
