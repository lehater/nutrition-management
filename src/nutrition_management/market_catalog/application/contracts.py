from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from nutrition_management.food_knowledge.application.contracts import NutrientFact


@dataclass(frozen=True)
class ExecutableOfferFact:
    offer_id: str
    sku_id: str
    base_food_id: str
    food_name: str
    category: str
    merchant_id: str
    channel_id: str
    fulfilment_mode: str
    edible_grams_per_package: Decimal
    package_price: Decimal
    currency: str
    minimum_order: Decimal
    fulfilment_fee: Decimal
    free_delivery_threshold: Decimal | None
    nutrients: tuple[NutrientFact, ...]
    observed_at: datetime
    valid_from: datetime | None
    valid_until: datetime | None
