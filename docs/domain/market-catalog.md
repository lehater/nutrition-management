# Market Catalog

Status: `accepted` for the current MVP tactical baseline.
Lifecycle layer: `S2 Domain Semantics / Tactical DDD`.

## Purpose

Own concrete commercial food products and the terms under which they can be purchased.

## Authoritative state

### Product Card / SKU

A concrete commercial food product linked to one Base Food.

A Product Card owns:
- commercial product identity;
- reference to Base Food;
- package size/quantity;
- product-specific nutrient overrides when known.

The effective nutrient profile used downstream is derived as:

`Base Food defaults + Product Card overrides`.

Missing override values fall back to the Base Food value. An override changes only the concrete SKU view and does not mutate Base Food truth.

### Merchant

A seller/store identity relevant to acquisition planning.

### Offer

A merchant-specific offer for one SKU.

An Offer owns:
- merchant;
- price;
- purchase/fulfilment method when material;
- delivery cost when applicable;
- minimum-order condition when applicable;
- other commercial terms that materially affect acquisition cost.

The same SKU may have multiple Offers at different merchants or under different conditions.

## Derived state

For comparison, package price and quantity may be normalized into comparable unit-cost measures. These are derived values; the observed Offer remains authoritative for the commercial terms.

## Invariants

- price belongs to an Offer, not to Base Food or SKU identity;
- package size belongs to the concrete Product Card/SKU;
- one SKU may be sold by multiple merchants at different prices;
- SKU nutrient overrides take precedence over Base Food defaults only where explicitly provided;
- acquisition conditions may affect the economic value of an Offer independently of unit price.

## MVP data acquisition

Product Cards and Offers may be entered manually or imported. Automatic price/store synchronization is not required.

## Explicit exclusions

Inventory ownership, household stock, leftover carry-over and travel/transport cost between merchants are outside the MVP.

## Material unknowns before architecture

- exact representation of fulfilment methods and merchant-level order conditions;
- price/offer validity semantics and timestamps;
- canonical units and conversion rules for package normalization.
