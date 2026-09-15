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


def _validate_instant(value: datetime | None, field: str) -> None:
    if value is not None and (value.tzinfo is None or value.utcoffset() is None):
        raise ValueError(f"{field} must be timezone-aware")


def _validate_interval(valid_from: datetime | None, valid_until: datetime | None) -> None:
    _validate_instant(valid_from, "valid_from")
    _validate_instant(valid_until, "valid_until")
    if valid_from is not None and valid_until is not None and valid_from > valid_until:
        raise ValueError("valid_from must not be later than valid_until")


@dataclass(frozen=True)
class NormalizedNutrientOverride:
    measure: str
    amount_per_100g: Decimal

    def __post_init__(self) -> None:
        if self.amount_per_100g < 0:
            raise ValueError("nutrient override amount must be non-negative")


@dataclass(frozen=True)
class ProductCard:
    sku_id: str
    base_food_id: str
    name: str
    edible_grams_per_package: Decimal
    nutrient_overrides: tuple[NormalizedNutrientOverride, ...] = ()

    def __post_init__(self) -> None:
        if self.edible_grams_per_package <= 0:
            raise ValueError("edible package quantity must be positive")


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

    def __post_init__(self) -> None:
        if self.minimum_order < 0:
            raise ValueError("minimum order must be non-negative")
        if self.fulfilment_fee < 0:
            raise ValueError("fulfilment fee must be non-negative")
        if self.free_delivery_threshold is not None and self.free_delivery_threshold < 0:
            raise ValueError("free-delivery threshold must be non-negative")
        if self.observed_at is None:
            raise ValueError("fulfilment channel observed_at is required")
        _validate_instant(self.observed_at, "observed_at")
        _validate_interval(self.valid_from, self.valid_until)

    def is_valid_at(self, at: datetime) -> bool:
        if self.observed_at > at:
            return False
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

    def __post_init__(self) -> None:
        if self.price < 0:
            raise ValueError("offer price must be non-negative")
        _validate_instant(self.observed_at, "observed_at")
        _validate_interval(self.valid_from, self.valid_until)

    def is_executable_at(self, at: datetime) -> bool:
        if self.availability != Availability.AVAILABLE:
            return False
        if self.observed_at > at:
            return False
        if self.valid_from is not None and at < self.valid_from:
            return False
        if self.valid_until is not None and at > self.valid_until:
            return False
        return True
