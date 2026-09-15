from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Column, ForeignKey, MetaData, String, Table, select

from nutrition_management.food_knowledge.application.contracts import (
    FoodFact,
    NutrientEvidenceStatus,
    NutrientFact,
)

metadata = MetaData()

food_table = Table(
    "fk_base_food",
    metadata,
    Column("base_food_id", String, primary_key=True),
    Column("name", String, nullable=False),
    Column("category", String, nullable=False),
    Column("source_name", String, nullable=False),
    Column("source_version", String),
)

nutrient_table = Table(
    "fk_nutrient_value",
    metadata,
    Column("base_food_id", String, ForeignKey("fk_base_food.base_food_id"), primary_key=True),
    Column("measure", String, primary_key=True),
    Column("status", String, nullable=False),
    Column("amount_per_100g", String),
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
