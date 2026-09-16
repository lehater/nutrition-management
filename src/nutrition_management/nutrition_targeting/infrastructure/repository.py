from __future__ import annotations

from datetime import date
from decimal import Decimal
import json

from sqlalchemy import Boolean, Column, ForeignKey, MetaData, String, Table, select

from nutrition_management.nutrition_targeting.domain.model import (
    AgeBoundary,
    AgeUnit,
    ApplicableWeightRule,
    ApplicabilityRequirement,
    MappingStatus,
    NutritionProfile,
    NutritionStandardSet,
    ReferenceApplicability,
    ReferenceBasis,
    ReferenceDefinition,
    ReferenceKind,
    ReferenceScope,
    SafetyDefinition,
    SafetyMapping,
    SafetySemanticKind,
    Sex,
    SourceSemanticKind,
    TargetMapping,
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
    Column("content_digest", String),
    Column("source_manifest", String),
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
    Column("family_id", String),
    Column("source_semantic_kind", String),
    Column("source_unit", String),
    Column("scope", String),
    Column("applicability_json", String),
    Column("applicable_weight_rule", String),
    Column("source_id", String),
    Column("source_locator", String),
    Column("lower_inclusive", Boolean, nullable=False, default=True),
    Column("upper_inclusive", Boolean, nullable=False, default=True),
)

mapping_table = Table(
    "nt_reference_mapping",
    metadata,
    Column("standard_version", String, ForeignKey("nt_standard_set.version"), primary_key=True),
    Column("family_id", String, primary_key=True),
    Column("status", String, nullable=False),
    Column("nutrient_measure", String),
    Column("canonical_unit", String),
    Column("formula_id", String),
    Column("reason", String),
)

safety_table = Table(
    "nt_safety_reference",
    metadata,
    Column("standard_version", String, ForeignKey("nt_standard_set.version"), primary_key=True),
    Column("reference_id", String, primary_key=True),
    Column("nutrient_measure", String, nullable=False),
    Column("daily_upper", String, nullable=False),
    Column("family_id", String),
    Column("semantic_kind", String),
    Column("source_unit", String),
    Column("scope", String),
    Column("applicability_json", String),
    Column("substance_scope", String),
    Column("source_id", String),
    Column("source_locator", String),
)

safety_mapping_table = Table(
    "nt_safety_mapping",
    metadata,
    Column("standard_version", String, ForeignKey("nt_standard_set.version"), primary_key=True),
    Column("family_id", String, primary_key=True),
    Column("status", String, nullable=False),
    Column("nutrient_measure", String),
    Column("canonical_unit", String),
    Column("reason", String),
)


def _decimal(value: str | None) -> Decimal | None:
    return None if value is None else Decimal(value)


def _boundary_json(value: AgeBoundary | None):
    return None if value is None else {"value": value.value, "unit": value.unit.value}


def _applicability_json(value: ReferenceApplicability) -> str:
    payload = {
        "min_age": _boundary_json(value.min_age),
        "max_age": _boundary_json(value.max_age),
        "sex": None if value.sex is None else value.sex.value,
        "requirements": [
            {"dimension": item.dimension, "value": item.value}
            for item in sorted(value.requirements, key=lambda item: item.dimension)
        ],
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _boundary(value) -> AgeBoundary | None:
    if value is None:
        return None
    return AgeBoundary(int(value["value"]), AgeUnit(value["unit"]))


def _applicability(value: str | None) -> ReferenceApplicability:
    if value is None:
        return ReferenceApplicability()
    raw = json.loads(value)
    return ReferenceApplicability(
        min_age=_boundary(raw.get("min_age")),
        max_age=_boundary(raw.get("max_age")),
        sex=None if raw.get("sex") is None else Sex(raw["sex"]),
        requirements=tuple(
            ApplicabilityRequirement(item["dimension"], item["value"])
            for item in raw.get("requirements", [])
        ),
    )


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

    def standard_digest(self, version: str) -> str | None:
        row = self._connection.execute(select(standard_table.c.content_digest).where(standard_table.c.version == version)).first()
        return None if row is None else row[0]

    def standard_exists(self, version: str) -> bool:
        return self._connection.execute(select(standard_table.c.version).where(standard_table.c.version == version)).first() is not None

    def activate_standard(self, version: str) -> None:
        if not self.standard_exists(version):
            raise ValueError(f"unknown standard version: {version}")
        self._connection.execute(standard_table.update().values(active=False))
        self._connection.execute(standard_table.update().where(standard_table.c.version == version).values(active=True))

    def add_standard(self, standard: NutritionStandardSet, *, active: bool = False, source_manifest: str | None = None) -> None:
        if active:
            self._connection.execute(standard_table.update().values(active=False))
        self._connection.execute(
            standard_table.insert().values(
                version=standard.version,
                active=active,
                content_digest=standard.content_digest,
                source_manifest=source_manifest,
            )
        )
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
                    family_id=ref.family_id,
                    source_semantic_kind=None if ref.source_semantic_kind is None else ref.source_semantic_kind.value,
                    source_unit=ref.source_unit,
                    scope=ref.scope.value,
                    applicability_json=_applicability_json(ref.applicability),
                    applicable_weight_rule=None if ref.applicable_weight_rule is None else ref.applicable_weight_rule.value,
                    source_id=ref.source_id,
                    source_locator=ref.source_locator,
                    lower_inclusive=ref.lower_inclusive,
                    upper_inclusive=ref.upper_inclusive,
                )
            )
        for item in standard.mappings:
            self._connection.execute(
                mapping_table.insert().values(
                    standard_version=standard.version,
                    family_id=item.family_id,
                    status=item.status.value,
                    nutrient_measure=item.nutrient_measure,
                    canonical_unit=item.canonical_unit,
                    formula_id=item.formula_id,
                    reason=item.reason,
                )
            )
        for item in standard.safety_limits:
            self._connection.execute(
                safety_table.insert().values(
                    reference_id=item.reference_id,
                    standard_version=standard.version,
                    nutrient_measure=item.nutrient_measure,
                    daily_upper=str(item.daily_upper),
                    family_id=item.family_id,
                    semantic_kind=item.semantic_kind.value,
                    source_unit=item.source_unit,
                    scope=item.scope.value,
                    applicability_json=_applicability_json(item.applicability),
                    substance_scope=item.substance_scope,
                    source_id=item.source_id,
                    source_locator=item.source_locator,
                )
            )
        for item in standard.safety_mappings:
            self._connection.execute(
                safety_mapping_table.insert().values(
                    standard_version=standard.version,
                    family_id=item.family_id,
                    status=item.status.value,
                    nutrient_measure=item.nutrient_measure,
                    canonical_unit=item.canonical_unit,
                    reason=item.reason,
                )
            )

    def active_standard(self) -> NutritionStandardSet:
        row = self._connection.execute(
            select(standard_table.c.version, standard_table.c.content_digest).where(standard_table.c.active.is_(True))
        ).one()
        version, digest = row
        refs = self._connection.execute(
            select(reference_table).where(reference_table.c.standard_version == version).order_by(reference_table.c.reference_id)
        ).mappings()
        mappings = self._connection.execute(
            select(mapping_table).where(mapping_table.c.standard_version == version).order_by(mapping_table.c.family_id)
        ).mappings()
        safety = self._connection.execute(
            select(safety_table).where(safety_table.c.standard_version == version).order_by(safety_table.c.reference_id)
        ).mappings()
        safety_mappings = self._connection.execute(
            select(safety_mapping_table).where(safety_mapping_table.c.standard_version == version).order_by(safety_mapping_table.c.family_id)
        ).mappings()
        return NutritionStandardSet(
            version=version,
            content_digest=digest,
            references=tuple(
                ReferenceDefinition(
                    reference_id=item["reference_id"],
                    nutrient_measure=item["nutrient_measure"],
                    kind=ReferenceKind(item["kind"]),
                    basis=ReferenceBasis(item["basis"]),
                    lower=_decimal(item["lower_value"]),
                    upper=_decimal(item["upper_value"]),
                    point=_decimal(item["point_value"]),
                    energy_kcal_per_g=_decimal(item["energy_kcal_per_g"]),
                    family_id=item["family_id"],
                    source_semantic_kind=None if item["source_semantic_kind"] is None else SourceSemanticKind(item["source_semantic_kind"]),
                    source_unit=item["source_unit"],
                    scope=ReferenceScope(item["scope"] or ReferenceScope.ACTIVE.value),
                    applicability=_applicability(item["applicability_json"]),
                    applicable_weight_rule=None if item["applicable_weight_rule"] is None else ApplicableWeightRule(item["applicable_weight_rule"]),
                    source_id=item["source_id"],
                    source_locator=item["source_locator"],
                    lower_inclusive=bool(item["lower_inclusive"]),
                    upper_inclusive=bool(item["upper_inclusive"]),
                )
                for item in refs
            ),
            mappings=tuple(
                TargetMapping(
                    family_id=item["family_id"],
                    status=MappingStatus(item["status"]),
                    nutrient_measure=item["nutrient_measure"],
                    canonical_unit=item["canonical_unit"],
                    formula_id=item["formula_id"],
                    reason=item["reason"],
                )
                for item in mappings
            ),
            safety_limits=tuple(
                SafetyDefinition(
                    reference_id=item["reference_id"],
                    nutrient_measure=item["nutrient_measure"],
                    daily_upper=Decimal(item["daily_upper"]),
                    family_id=item["family_id"],
                    semantic_kind=SafetySemanticKind(item["semantic_kind"] or SafetySemanticKind.UL.value),
                    source_unit=item["source_unit"],
                    scope=ReferenceScope(item["scope"] or ReferenceScope.ACTIVE.value),
                    applicability=_applicability(item["applicability_json"]),
                    substance_scope=item["substance_scope"],
                    source_id=item["source_id"],
                    source_locator=item["source_locator"],
                )
                for item in safety
            ),
            safety_mappings=tuple(
                SafetyMapping(
                    family_id=item["family_id"],
                    status=MappingStatus(item["status"]),
                    nutrient_measure=item["nutrient_measure"],
                    canonical_unit=item["canonical_unit"],
                    reason=item["reason"],
                )
                for item in safety_mappings
            ),
        )
