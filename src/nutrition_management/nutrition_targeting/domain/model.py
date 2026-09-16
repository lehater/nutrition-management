from __future__ import annotations

from calendar import monthrange
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import StrEnum


class UnsupportedSliceCapability(ValueError):
    """Accepted product behavior that is intentionally outside the authorized slice."""


class Sex(StrEnum):
    FEMALE = "female"
    MALE = "male"


class ReferenceKind(StrEnum):
    ADEQUACY_FLOOR = "adequacy_floor"
    LOWER_BOUND = "lower_bound"
    UPPER_BOUND = "upper_bound"
    INTERVAL = "interval"
    POINT = "point"


class ReferenceBasis(StrEnum):
    ABSOLUTE_DAILY = "absolute_daily"
    PER_KG_DAILY = "per_kg_daily"
    PERCENT_ENERGY = "percent_energy"
    PER_1000_KCAL = "per_1000_kcal"


class SourceSemanticKind(StrEnum):
    RECOMMENDED_INTAKE = "recommended_intake"
    ESTIMATED_VALUE = "estimated_value"
    GUIDELINE = "guideline"
    UNCLASSIFIED = "unclassified"


class ReferenceScope(StrEnum):
    ACTIVE = "active"
    OUTSIDE_MVP_SCOPE = "outside_mvp_scope"
    NON_ACTIVE = "non_active"


class AgeUnit(StrEnum):
    MONTHS = "months"
    YEARS = "years"


class ApplicableWeightRule(StrEnum):
    CURRENT_WEIGHT = "current_weight"
    DGE_ADULT_PROTEIN = "dge_adult_protein"


class MappingStatus(StrEnum):
    MAPPED = "mapped"
    UNSUPPORTED = "unsupported"


class ReferenceGapState(StrEnum):
    UNSUPPORTED_APPLICABILITY = "unsupported_applicability"
    SOURCE_INAPPLICABLE = "source_inapplicable"
    UNSUPPORTED_MAPPING = "unsupported_mapping"
    UNSUPPORTED_TARGET_SHAPE = "unsupported_target_shape"


class SafetyGapState(StrEnum):
    UNSUPPORTED_APPLICABILITY = "unsupported_applicability"
    SOURCE_INAPPLICABLE = "source_inapplicable"
    UNSUPPORTED_MAPPING = "unsupported_mapping"


class SafetySemanticKind(StrEnum):
    UL = "ul"
    SAFE_LEVEL = "safe_level"


@dataclass(frozen=True)
class AgeBoundary:
    value: int
    unit: AgeUnit

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("age boundary must be non-negative")


@dataclass(frozen=True)
class ApplicabilityRequirement:
    dimension: str
    value: str

    def __post_init__(self) -> None:
        if not self.dimension or not self.value:
            raise ValueError("applicability requirement dimension and value are required")


@dataclass(frozen=True)
class ReferenceApplicability:
    min_age: AgeBoundary | None = None
    max_age: AgeBoundary | None = None
    sex: Sex | None = None
    requirements: tuple[ApplicabilityRequirement, ...] = ()

    def __post_init__(self) -> None:
        dimensions = [item.dimension for item in self.requirements]
        if len(dimensions) != len(set(dimensions)):
            raise ValueError("applicability requirement dimensions must be unique")
        if self.min_age is not None and self.max_age is not None and self.min_age.unit == self.max_age.unit:
            if self.min_age.value >= self.max_age.value:
                raise ValueError("age applicability lower bound must be below upper bound")


@dataclass(frozen=True)
class NutritionProfile:
    member_id: str
    date_of_birth: date
    sex: Sex
    height_m: Decimal
    current_weight_kg: Decimal
    current_weight_date: date
    pal: Decimal
    pal_activity_adjustment_applied: bool = False
    target_weight_kg: Decimal | None = None
    target_date: date | None = None

    def __post_init__(self) -> None:
        if self.height_m <= 0:
            raise ValueError("height must be positive")
        if self.current_weight_kg <= 0:
            raise ValueError("current weight must be positive")
        if self.target_weight_kg is not None and self.target_weight_kg <= 0:
            raise ValueError("target weight must be positive")


@dataclass(frozen=True)
class ReferenceDefinition:
    reference_id: str
    nutrient_measure: str
    kind: ReferenceKind
    basis: ReferenceBasis
    lower: Decimal | None = None
    upper: Decimal | None = None
    point: Decimal | None = None
    energy_kcal_per_g: Decimal | None = None
    family_id: str | None = None
    source_semantic_kind: SourceSemanticKind | None = None
    source_unit: str | None = None
    scope: ReferenceScope = ReferenceScope.ACTIVE
    applicability: ReferenceApplicability = field(default_factory=ReferenceApplicability)
    applicable_weight_rule: ApplicableWeightRule | None = None
    source_id: str | None = None
    source_locator: str | None = None
    lower_inclusive: bool = True
    upper_inclusive: bool = True

    @property
    def resolved_family_id(self) -> str:
        return self.reference_id if self.family_id is None else self.family_id

    @property
    def has_open_bound(self) -> bool:
        return (self.lower is not None and not self.lower_inclusive) or (self.upper is not None and not self.upper_inclusive)

    def __post_init__(self) -> None:
        if not self.reference_id or not self.nutrient_measure:
            raise ValueError("reference identity and nutrient measure are required")
        if self.family_id == "":
            raise ValueError("family identity must not be empty")
        if self.source_unit == "":
            raise ValueError("source unit must not be empty")
        for value in (self.lower, self.upper, self.point):
            if value is not None and value < 0:
                raise ValueError("reference values must be non-negative")
        if not isinstance(self.lower_inclusive, bool) or not isinstance(self.upper_inclusive, bool):
            raise ValueError("bound inclusivity flags must be boolean")
        if self.lower is None and not self.lower_inclusive:
            raise ValueError("open lower bound requires a lower value")
        if self.upper is None and not self.upper_inclusive:
            raise ValueError("open upper bound requires an upper value")

        if self.kind in {ReferenceKind.ADEQUACY_FLOOR, ReferenceKind.LOWER_BOUND}:
            if self.lower is None or self.lower <= 0 or self.upper is not None or self.point is not None:
                raise ValueError("lower-bound reference requires only a positive lower value")
        elif self.kind == ReferenceKind.UPPER_BOUND:
            if self.upper is None or self.upper <= 0 or self.lower is not None or self.point is not None:
                raise ValueError("upper-bound reference requires only a positive upper value")
        elif self.kind == ReferenceKind.INTERVAL:
            if self.lower is None or self.upper is None or self.lower <= 0 or self.upper <= 0 or self.lower > self.upper or self.point is not None:
                raise ValueError("interval reference requires a positive ordered lower/upper pair")
        elif self.kind == ReferenceKind.POINT:
            if self.point is None or self.point <= 0 or self.lower is not None or self.upper is not None:
                raise ValueError("point reference requires only a positive point value")

        if self.basis == ReferenceBasis.PERCENT_ENERGY:
            if self.energy_kcal_per_g is None or self.energy_kcal_per_g <= 0:
                raise ValueError("percent-energy reference requires a positive energy factor")
        elif self.energy_kcal_per_g is not None:
            raise ValueError("energy factor is only valid for percent-energy references")

        if self.basis == ReferenceBasis.PER_KG_DAILY and self.applicable_weight_rule is None:
            object.__setattr__(self, "applicable_weight_rule", ApplicableWeightRule.CURRENT_WEIGHT)
        elif self.basis != ReferenceBasis.PER_KG_DAILY and self.applicable_weight_rule is not None:
            raise ValueError("applicable weight rule is only valid for per-kg references")


@dataclass(frozen=True)
class TargetMapping:
    family_id: str
    status: MappingStatus
    nutrient_measure: str | None = None
    canonical_unit: str | None = None
    formula_id: str | None = None
    reason: str | None = None

    def __post_init__(self) -> None:
        if not self.family_id:
            raise ValueError("mapping family identity is required")
        if self.status == MappingStatus.MAPPED:
            if not self.nutrient_measure or not self.canonical_unit:
                raise ValueError("mapped reference requires canonical measure and unit")
            if self.reason is not None:
                raise ValueError("mapped reference must not carry unsupported reason")
        else:
            if not self.reason:
                raise ValueError("unsupported mapping requires a reason")
            if self.nutrient_measure is not None or self.canonical_unit is not None or self.formula_id is not None:
                raise ValueError("unsupported mapping must not carry canonical mapping fields")


@dataclass(frozen=True)
class SafetyMapping:
    family_id: str
    status: MappingStatus
    nutrient_measure: str | None = None
    canonical_unit: str | None = None
    reason: str | None = None

    def __post_init__(self) -> None:
        if not self.family_id:
            raise ValueError("safety mapping family identity is required")
        if self.status == MappingStatus.MAPPED:
            if not self.nutrient_measure or not self.canonical_unit:
                raise ValueError("mapped safety limit requires canonical measure and unit")
            if self.reason is not None:
                raise ValueError("mapped safety limit must not carry unsupported reason")
        else:
            if not self.reason:
                raise ValueError("unsupported safety mapping requires a reason")
            if self.nutrient_measure is not None or self.canonical_unit is not None:
                raise ValueError("unsupported safety mapping must not carry canonical mapping fields")


@dataclass(frozen=True)
class SafetyDefinition:
    reference_id: str
    nutrient_measure: str
    daily_upper: Decimal
    family_id: str | None = None
    semantic_kind: SafetySemanticKind = SafetySemanticKind.UL
    source_unit: str | None = None
    scope: ReferenceScope = ReferenceScope.ACTIVE
    applicability: ReferenceApplicability = field(default_factory=ReferenceApplicability)
    substance_scope: str | None = None
    source_id: str | None = None
    source_locator: str | None = None

    @property
    def resolved_family_id(self) -> str:
        return self.reference_id if self.family_id is None else self.family_id

    def __post_init__(self) -> None:
        if not self.reference_id or not self.nutrient_measure:
            raise ValueError("safety reference identity and nutrient measure are required")
        if self.daily_upper <= 0:
            raise ValueError("safety daily upper must be positive")
        if self.family_id == "" or self.source_unit == "" or self.substance_scope == "":
            raise ValueError("safety semantic metadata must not be empty")


@dataclass(frozen=True)
class NutritionStandardSet:
    version: str
    references: tuple[ReferenceDefinition, ...]
    safety_limits: tuple[SafetyDefinition, ...] = ()
    mappings: tuple[TargetMapping, ...] = ()
    content_digest: str | None = None
    safety_mappings: tuple[SafetyMapping, ...] = ()

    def __post_init__(self) -> None:
        if not self.version:
            raise ValueError("standard version is required")
        reference_ids = [item.reference_id for item in self.references]
        safety_ids = [item.reference_id for item in self.safety_limits]
        mapping_ids = [item.family_id for item in self.mappings]
        safety_mapping_ids = [item.family_id for item in self.safety_mappings]
        if len(reference_ids) != len(set(reference_ids)):
            raise ValueError("reference ids must be unique within a standard version")
        if len(safety_ids) != len(set(safety_ids)):
            raise ValueError("safety reference ids must be unique within a standard version")
        if len(mapping_ids) != len(set(mapping_ids)):
            raise ValueError("mapping family ids must be unique within a standard version")
        if len(safety_mapping_ids) != len(set(safety_mapping_ids)):
            raise ValueError("safety mapping family ids must be unique within a standard version")
        if self.content_digest is not None and not self.content_digest:
            raise ValueError("content digest must not be empty")
        if self.mappings:
            active_families = {item.resolved_family_id for item in self.references if item.scope == ReferenceScope.ACTIVE}
            if set(mapping_ids) != active_families:
                missing = sorted(active_families - set(mapping_ids))
                extra = sorted(set(mapping_ids) - active_families)
                raise ValueError(f"mapping registry must cover active families exactly; missing={missing}, extra={extra}")
        if self.safety_mappings:
            active_safety_families = {item.resolved_family_id for item in self.safety_limits if item.scope == ReferenceScope.ACTIVE}
            if set(safety_mapping_ids) != active_safety_families:
                missing = sorted(active_safety_families - set(safety_mapping_ids))
                extra = sorted(set(safety_mapping_ids) - active_safety_families)
                raise ValueError(f"safety mapping registry must cover active families exactly; missing={missing}, extra={extra}")

    def mapping_for_family(self, family_id: str) -> TargetMapping | None:
        return next((item for item in self.mappings if item.family_id == family_id), None)

    def safety_mapping_for_family(self, family_id: str) -> SafetyMapping | None:
        return next((item for item in self.safety_mappings if item.family_id == family_id), None)


@dataclass(frozen=True)
class ReferenceGap:
    member_id: str
    family_id: str
    state: ReferenceGapState
    missing_dimensions: tuple[str, ...] = ()
    candidate_reference_ids: tuple[str, ...] = ()
    reason: str | None = None


@dataclass(frozen=True)
class SafetyGap:
    member_id: str
    family_id: str
    state: SafetyGapState
    missing_dimensions: tuple[str, ...] = ()
    candidate_reference_ids: tuple[str, ...] = ()
    reason: str | None = None


@dataclass(frozen=True)
class ResolvedReference:
    reference_id: str
    nutrient_measure: str
    kind: ReferenceKind
    lower_30d: Decimal | None = None
    upper_30d: Decimal | None = None
    point_30d: Decimal | None = None
    family_id: str | None = None


@dataclass(frozen=True)
class MemberSafetyLimit:
    member_id: str
    reference_id: str
    nutrient_measure: str
    daily_upper: Decimal


@dataclass(frozen=True)
class MemberNutritionTarget:
    member_id: str
    derivation_date: date
    standard_version: str
    age_years: int
    current_weight_kg: Decimal
    current_weight_date: date
    pal: Decimal
    pal_activity_adjustment_applied: bool
    energy_kcal_30d: Decimal
    references: tuple[ResolvedReference, ...]
    safety_limits: tuple[MemberSafetyLimit, ...]
    reference_gaps: tuple[ReferenceGap, ...] = ()
    safety_gaps: tuple[SafetyGap, ...] = ()


@dataclass(frozen=True)
class HouseholdNutritionTarget:
    household_id: str
    derivation_date: date
    standard_version: str
    energy_kcal_30d: Decimal
    references: tuple[ResolvedReference, ...]
    member_targets: tuple[MemberNutritionTarget, ...]
    reference_gaps: tuple[ReferenceGap, ...] = ()
    safety_gaps: tuple[SafetyGap, ...] = ()


def chronological_age_years(date_of_birth: date, on_date: date) -> int:
    if date_of_birth > on_date:
        raise ValueError("date_of_birth must not be later than derivation date")
    years = on_date.year - date_of_birth.year
    if (on_date.month, on_date.day) < (date_of_birth.month, date_of_birth.day):
        years -= 1
    return years


def completed_calendar_months(date_of_birth: date, on_date: date) -> int:
    if date_of_birth > on_date:
        raise ValueError("date_of_birth must not be later than derivation date")
    months = (on_date.year - date_of_birth.year) * 12 + on_date.month - date_of_birth.month
    anniversary_day = min(date_of_birth.day, monthrange(on_date.year, on_date.month)[1])
    if on_date.day < anniversary_day:
        months -= 1
    return months