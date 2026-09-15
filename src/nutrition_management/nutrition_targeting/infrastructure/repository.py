from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Column, ForeignKey, MetaData, String, Table, select

from nutrition_management.nutrition_targeting.domain.model import (
    NutritionProfile,
    NutritionStandardSet,
    ReferenceBasis,
    ReferenceDefinition,
    ReferenceKind,
    SafetyDefinition,
    Sex,
)

metadata = MetaData()

member_table = Table(
    "nt_member_profile",
    metadata,
    Column("member_id", String, primary_key=True),
    Column("household_id", String, nullable=False, index=True),
    Column("date_of_birth", String, nullable=False),
    Column("sex", String, nullable=False),
    Column("height_m", String, nullable=False),
    Column("current_weight_kg", String, nullable=False),
    Column("current_weight_date", String, nullable=False),
    Column("pal", String, nullable=False),
    Column("pal_activity_adjustment_applied", Boolean, nullable=False),
    Column("target_weight_kg", String),
    Column("target_date", String),
)

standard_table = Table(
    "nt_standard_set",
    metadata,
    Column("version", String, primary_key=True),
    Column("active", Boolean, nullable=False, default=False),
)

reference_table = Table(
    "nt_standard_reference",
    metadata,
    Column("standard_version", String, ForeignKey("nt_standard_set.version"), primary_key=True),
    Column("reference_id", String, primary_key=True),
    Column("nutrient_measure", String, nullable=False),
    Column("kind", String, nullable=False),
    Column("basis", String, nullable=False),
    Column("lower_value", String),
    Column("upper_value", String),
    Column("point_value", String),
    Column("energy_kcal_per_g", String),
)

safety_table = Table(
    "nt_safety_reference",
    metadata,
    Column("standard_version", String, ForeignKey("nt_standard_set.version"), primary_key=True),
    Column("reference_id", String, primary_key=True),
    Column("nutrient_measure", String, nullable=False),
    Column("daily_upper", String, nullable=False),
)


def _decimal(value: str | None) -> Decimal | None:
    return None if value is None else Decimal(value)


class NutritionTargetingRepository:
    def __init__(self, connection):
        self._connection = connection

    def add_profile(self, household_id: str, profile: NutritionProfile) -> None:
        self._connection.execute(
            member_table.insert().values(
                member_id=profile.member_id,
                household_id=household_id,
                date_of_birth=profile.date_of_birth.isoformat(),
                sex=profile.sex.value,
                height_m=str(profile.height_m),
                current_weight_kg=str(profile.current_weight_kg),
                current_weight_date=profile.current_weight_date.isoformat(),
                pal=str(profile.pal),
                pal_activity_adjustment_applied=profile.pal_activity_adjustment_applied,
                target_weight_kg=None if profile.target_weight_kg is None else str(profile.target_weight_kg),
                target_date=None if profile.target_date is None else profile.target_date.isoformat(),
            )
        )

    def profiles_for_household(self, household_id: str) -> tuple[NutritionProfile, ...]:
        rows = self._connection.execute(
            select(member_table).where(member_table.c.household_id == household_id).order_by(member_table.c.member_id)
        ).mappings()
        return tuple(
            NutritionProfile(
                member_id=row["member_id"],
                date_of_birth=date.fromisoformat(row["date_of_birth"]),
                sex=Sex(row["sex"]),
                height_m=Decimal(row["height_m"]),
                current_weight_kg=Decimal(row["current_weight_kg"]),
                current_weight_date=date.fromisoformat(row["current_weight_date"]),
                pal=Decimal(row["pal"]),
                pal_activity_adjustment_applied=bool(row["pal_activity_adjustment_applied"]),
                target_weight_kg=_decimal(row["target_weight_kg"]),
                target_date=None if row["target_date"] is None else date.fromisoformat(row["target_date"]),
            )
            for row in rows
        )

    def add_standard(self, standard: NutritionStandardSet, *, active: bool = False) -> None:
        if active:
            self._connection.execute(standard_table.update().values(active=False))
        self._connection.execute(standard_table.insert().values(version=standard.version, active=active))
        for ref in standard.references:
            self._connection.execute(
                reference_table.insert().values(
                    reference_id=ref.reference_id,
                    standard_version=standard.version,
                    nutrient_measure=ref.nutrient_measure,
                    kind=ref.kind.value,
                    basis=ref.basis.value,
                    lower_value=None if ref.lower is None else str(ref.lower),
                    upper_value=None if ref.upper is None else str(ref.upper),
                    point_value=None if ref.point is None else str(ref.point),
                    energy_kcal_per_g=None if ref.energy_kcal_per_g is None else str(ref.energy_kcal_per_g),
                )
            )
        for item in standard.safety_limits:
            self._connection.execute(
                safety_table.insert().values(
                    reference_id=item.reference_id,
                    standard_version=standard.version,
                    nutrient_measure=item.nutrient_measure,
                    daily_upper=str(item.daily_upper),
                )
            )

    def active_standard(self) -> NutritionStandardSet:
        version = self._connection.execute(
            select(standard_table.c.version).where(standard_table.c.active.is_(True))
        ).scalar_one()
        refs = self._connection.execute(
            select(reference_table).where(reference_table.c.standard_version == version).order_by(reference_table.c.reference_id)
        ).mappings()
        safety = self._connection.execute(
            select(safety_table).where(safety_table.c.standard_version == version).order_by(safety_table.c.reference_id)
        ).mappings()
        return NutritionStandardSet(
            version=version,
            references=tuple(
                ReferenceDefinition(
                    reference_id=row["reference_id"],
                    nutrient_measure=row["nutrient_measure"],
                    kind=ReferenceKind(row["kind"]),
                    basis=ReferenceBasis(row["basis"]),
                    lower=_decimal(row["lower_value"]),
                    upper=_decimal(row["upper_value"]),
                    point=_decimal(row["point_value"]),
                    energy_kcal_per_g=_decimal(row["energy_kcal_per_g"]),
                )
                for row in refs
            ),
            safety_limits=tuple(
                SafetyDefinition(
                    reference_id=row["reference_id"],
                    nutrient_measure=row["nutrient_measure"],
                    daily_upper=Decimal(row["daily_upper"]),
                )
                for row in safety
            ),
        )
