from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum


class Availability(StrEnum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


class FulfilmentMode(StrEnum):
    PICKUP = "pickup"
    DELIVERY = "delivery"


@dataclass(frozen=True)
class NormalizedNutrientOverride:
    measure: str
    amount_per_100g: Decimal


@dataclass(frozen=True)
class ProductCard:
    sku_id: str
    base_food_id: str
    name: str
    edible_grams_per_package: Decimal
    nutrient_overrides: tuple[NormalizedNutrientOverride, ...] = ()


@dataclass(frozen=True)
class FulfilmentChannel:
    channel_id: str
    merchant_id: str
    mode: FulfilmentMode
    currency: str
    minimum_order: Decimal = Decimal(0)
    fulfilment_fee: Decimal = Decimal(0)
    free_delivery_threshold: Decimal | None = None
    observed_at: datetime | None = None
    valid_from: datetime | None = None
    valid_until: datetime | None = None

    def is_valid_at(self, at: datetime) -> bool:
        if self.valid_from is not None and at < self.valid_from:
            return False
        if self.valid_until is not None and at > self.valid_until:
            return False
        return True


@dataclass(frozen=True)
class Offer:
    offer_id: str
    sku_id: str
    channel_id: str
    price: Decimal
    currency: str
    availability: Availability
    observed_at: datetime
    valid_from: datetime | None = None
    valid_until: datetime | None = None

    def is_executable_at(self, at: datetime) -> bool:
        if self.availability != Availability.AVAILABLE:
            return False
        if self.valid_from is not None and at < self.valid_from:
            return False
        if self.valid_until is not None and at > self.valid_until:
            return False
        return True
