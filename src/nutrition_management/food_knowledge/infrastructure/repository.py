from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Column, ForeignKey, MetaData, String, Table, select

from nutrition_management.food_knowledge.application.contracts import (
    FoodFact,
    NutrientEvidenceStatus,
    NutrientFact,
)
from nutrition_management.food_knowledge.application.source_data import FoodSourceDataset

metadata = MetaData()

source_dataset_table = Table(
    "fk_source_dataset",
    metadata,
    Column("source_id", String, primary_key=True),
    Column("source_name", String, nullable=False),
    Column("source_version", String, nullable=False),
    Column("source_digest", String, nullable=False),
    Column("package_digest", String, nullable=False),
    Column("doi", String, nullable=False),
    Column("license", String, nullable=False),
    Column("source_url", String, nullable=False),
    Column("attribution", String, nullable=False),
    Column("manifest_json", String, nullable=False),
)

component_table = Table(
    "fk_component",
    metadata,
    Column("source_id", String, ForeignKey("fk_source_dataset.source_id"), primary_key=True),
    Column("component_code", String, primary_key=True),
    Column("name_de", String, nullable=False),
    Column("name_en", String, nullable=False),
    Column("unit", String, nullable=False),
    Column("group_de", String),
    Column("group_en", String),
    Column("formula", String),
    Column("formula_application", String),
)

food_table = Table(
    "fk_base_food",
    metadata,
    Column("base_food_id", String, primary_key=True),
    Column("name", String, nullable=False),
    Column("category", String, nullable=False),
    Column("source_name", String, nullable=False),
    Column("source_version", String),
    Column("source_id", String),
    Column("source_code", String),
    Column("name_en", String),
)

nutrient_table = Table(
    "fk_nutrient_value",
    metadata,
    Column("base_food_id", String, ForeignKey("fk_base_food.base_food_id"), primary_key=True),
    Column("measure", String, primary_key=True),
    Column("status", String, nullable=False),
    Column("amount_per_100g", String),
    Column("source_value_text", String),
    Column("value_origin", String),
    Column("source_reference", String),
)


class FoodKnowledgeRepository:
    def __init__(self, connection):
        self._connection = connection

    def add_food(self, food: FoodFact) -> None:
        self._connection.execute(
            food_table.insert().values(
                base_food_id=food.base_food_id,
                name=food.name,
                category=food.category,
                source_name=food.source_name,
                source_version=food.source_version,
            )
        )
        for item in food.nutrients:
            self._connection.execute(
                nutrient_table.insert().values(
                    base_food_id=food.base_food_id,
                    measure=item.measure,
                    status=item.status.value,
                    amount_per_100g=None if item.amount_per_100g is None else str(item.amount_per_100g),
                )
            )

    def source_dataset_digests(self, source_id: str) -> tuple[str, str] | None:
        row = self._connection.execute(
            select(
                source_dataset_table.c.source_digest,
                source_dataset_table.c.package_digest,
            ).where(source_dataset_table.c.source_id == source_id)
        ).one_or_none()
        if row is None:
            return None
        return row.source_digest, row.package_digest

    def add_source_dataset(self, dataset: FoodSourceDataset, *, manifest_json: str) -> None:
        self._connection.execute(
            source_dataset_table.insert().values(
                source_id=dataset.source_id,
                source_name=dataset.source_name,
                source_version=dataset.source_version,
                source_digest=dataset.source_digest,
                package_digest=dataset.package_digest,
                doi=dataset.doi,
                license=dataset.license,
                source_url=dataset.source_url,
                attribution=dataset.attribution,
                manifest_json=manifest_json,
            )
        )
        for component in dataset.components:
            self._connection.execute(
                component_table.insert().values(
                    source_id=dataset.source_id,
                    component_code=component.component_code,
                    name_de=component.name_de,
                    name_en=component.name_en,
                    unit=component.unit,
                    group_de=component.group_de,
                    group_en=component.group_en,
                    formula=component.formula,
                    formula_application=component.formula_application,
                )
            )
        for food in dataset.foods:
            self._connection.execute(
                food_table.insert().values(
                    base_food_id=food.base_food_id,
                    name=food.name_de,
                    category=food.category,
                    source_name=dataset.source_name,
                    source_version=dataset.source_version,
                    source_id=dataset.source_id,
                    source_code=food.source_code,
                    name_en=food.name_en,
                )
            )
            for item in food.nutrients:
                self._connection.execute(
                    nutrient_table.insert().values(
                        base_food_id=food.base_food_id,
                        measure=item.component_code,
                        status=item.status.value,
                        amount_per_100g=None if item.amount_per_100g is None else str(item.amount_per_100g),
                        source_value_text=item.source_value_text,
                        value_origin=item.value_origin,
                        source_reference=item.source_reference,
                    )
                )

    def get_food(self, base_food_id: str) -> FoodFact:
        row = self._connection.execute(
            select(food_table).where(food_table.c.base_food_id == base_food_id)
        ).mappings().one()
        nutrient_rows = self._connection.execute(
            select(nutrient_table)
            .where(nutrient_table.c.base_food_id == base_food_id)
            .order_by(nutrient_table.c.measure)
        ).mappings()
        return FoodFact(
            base_food_id=row["base_food_id"],
            name=row["name"],
            category=row["category"],
            source_name=row["source_name"],
            source_version=row["source_version"],
            nutrients=tuple(
                NutrientFact(
                    measure=item["measure"],
                    status=NutrientEvidenceStatus(item["status"]),
                    amount_per_100g=None if item["amount_per_100g"] is None else Decimal(item["amount_per_100g"]),
                )
                for item in nutrient_rows
            ),
        )

    def all_foods(self) -> tuple[FoodFact, ...]:
        ids = self._connection.execute(select(food_table.c.base_food_id).order_by(food_table.c.base_food_id)).scalars()
        return tuple(self.get_food(item) for item in ids)
