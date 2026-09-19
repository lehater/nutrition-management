from __future__ import annotations

from datetime import UTC, date, datetime

from nutrition_management.food_knowledge.infrastructure.repository import FoodKnowledgeRepository
from nutrition_management.market_catalog.application.service import executable_market_projection
from nutrition_management.market_catalog.infrastructure.repository import MarketCatalogRepository
from nutrition_management.nutrition_targeting.application.service import derive_household_target_fact
from nutrition_management.nutrition_targeting.infrastructure.repository import NutritionTargetingRepository
from nutrition_management.purchase_planning.application.ports import PlanningSnapshotSource
from nutrition_management.purchase_planning.domain.model import (
    CandidateNutrient,
    EvidenceStatus,
    MemberSafetyLimit,
    PlanningInputSnapshot,
    PurchaseCandidate,
    SafetyCoverageGap,
    TargetCoverageGap,
    TargetDimension,
    TargetKind,
    TargetMemberProvenance,
)

POLICY_VERSION = "ADR-007-v1"


class SqlitePlanningSnapshotSource(PlanningSnapshotSource):
    def __init__(self, engine):
        self._engine = engine

    def capture(self, household_id: str, derivation_date: date, market_as_of: datetime) -> PlanningInputSnapshot:
        if market_as_of.tzinfo is None or market_as_of.utcoffset() is None:
            raise ValueError("market_as_of must be timezone-aware")
        market_as_of = market_as_of.astimezone(UTC)

        with self._engine.connect() as connection:
            transaction = connection.begin()
            try:
                nt_repo = NutritionTargetingRepository(connection)
                fk_repo = FoodKnowledgeRepository(connection)
                mc_repo = MarketCatalogRepository(connection)

                target = derive_household_target_fact(nt_repo, household_id, derivation_date)
                market = executable_market_projection(
                    products=mc_repo.products(),
                    channels=mc_repo.channels(),
                    offers=mc_repo.offers(),
                    food_lookup=fk_repo.get_food,
                    as_of=market_as_of,
                )

                snapshot = PlanningInputSnapshot(
                    household_id=household_id,
                    derivation_date=derivation_date,
                    market_as_of=market_as_of,
                    standard_version=target.standard_version,
                    policy_version=POLICY_VERSION,
                    energy_target_kcal=target.energy_kcal_30d,
                    targets=tuple(
                        TargetDimension(
                            measure=item.measure,
                            kind=TargetKind(item.kind),
                            lower=item.lower_30d,
                            upper=item.upper_30d,
                            point=item.point_30d,
                        )
                        for item in target.targets
                    ),
                    member_safety_limits=tuple(
                        MemberSafetyLimit(
                            member_id=item.member_id,
                            reference_id=item.reference_id,
                            measure=item.measure,
                            daily_upper=item.daily_upper,
                        )
                        for item in target.member_safety_limits
                    ),
                    target_member_provenance=tuple(
                        TargetMemberProvenance(
                            member_id=item.member_id,
                            age_years=item.age_years,
                            current_weight_kg=item.current_weight_kg,
                            current_weight_date=item.current_weight_date,
                            pal=item.pal,
                            pal_activity_adjustment_applied=item.pal_activity_adjustment_applied,
                        )
                        for item in target.member_provenance
                    ),
                    target_coverage_gaps=tuple(
                        TargetCoverageGap(
                            member_id=item.member_id,
                            family_id=item.family_id,
                            state=item.state,
                            missing_dimensions=item.missing_dimensions,
                            candidate_reference_ids=item.candidate_reference_ids,
                            reason=item.reason,
                        )
                        for item in target.target_coverage_gaps
                    ),
                    safety_coverage_gaps=tuple(
                        SafetyCoverageGap(
                            member_id=item.member_id,
                            family_id=item.family_id,
                            state=item.state,
                            reason=item.reason,
                        )
                        for item in target.safety_coverage_gaps
                    ),
                    candidates=tuple(
                        PurchaseCandidate(
                            offer_id=item.offer_id,
                            sku_id=item.sku_id,
                            base_food_id=item.base_food_id,
                            food_name=item.food_name,
                            category=item.category,
                            merchant_id=item.merchant_id,
                            channel_id=item.channel_id,
                            fulfilment_mode=item.fulfilment_mode,
                            edible_grams_per_package=item.edible_grams_per_package,
                            package_price=item.package_price,
                            currency=item.currency,
                            minimum_order=item.minimum_order,
                            fulfilment_fee=item.fulfilment_fee,
                            free_delivery_threshold=item.free_delivery_threshold,
                            nutrients=tuple(
                                CandidateNutrient(
                                    measure=nutrient.measure,
                                    status=EvidenceStatus(nutrient.status.value),
                                    amount_per_100g=nutrient.amount_per_100g,
                                )
                                for nutrient in item.nutrients
                            ),
                            observed_at=item.observed_at,
                            valid_from=item.valid_from,
                            valid_until=item.valid_until,
                        )
                        for item in market
                    ),
                )
            finally:
                transaction.rollback()
        return snapshot
