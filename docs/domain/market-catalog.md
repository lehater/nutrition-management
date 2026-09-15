# Market Catalog

Status: `accepted` for the current MVP tactical baseline.
Lifecycle layer: `S2 Domain Semantics / Tactical DDD`.

## Purpose

Own concrete commercial food products and the terms under which they can be purchased.

Commercial Offer/Fulfilment semantics are accepted by [`ADR-006`](../decisions/ADR-006-market-offer-and-fulfilment-semantics.md).

## Authoritative state

### Product Card / SKU

A concrete commercial food product linked to one Base Food.

A Product Card owns:
- commercial product identity;
- reference to Base Food;
- package size/quantity;
- edible-quantity conversion required for nutritional calculation when package units are not directly mass-based;
- product-specific nutrient overrides when known.

The effective nutrient profile used downstream is derived as:

`Base Food defaults + normalized Product Card overrides`.

A nutrient override can replace a Base Food component only after normalization to the canonical nutrient identity, unit and `100 g edible portion` basis defined by Food Knowledge. Missing override values fall back to the Base Food value component-by-component. An override changes only the concrete SKU view and does not mutate Base Food truth.

A source label value expressed per 100 ml, per serving or per package is not yet a canonical override unless the Product Card has enough quantity semantics to convert it to the per-100-g edible basis.

### Executable edible quantity

For quantitative nutrition optimization, one purchasable package must resolve to edible grams.

This may be provided by:
- direct edible/net food mass;
- density or another accepted volume-to-mass conversion;
- edible unit mass for count-based packages;
- another explicit conversion that yields edible mass without guessing.

If a Product Card lacks such a conversion, it may remain catalog knowledge but cannot participate in an executable nutrition calculation.

### Merchant

A seller identity relevant to acquisition planning.

### Fulfilment Channel

A concrete acquisition context for one Merchant through which multiple SKU Offers can be purchased together under shared order conditions.

MVP modes:
- `pickup`;
- `delivery`.

A Merchant may have several channels when store/location or delivery conditions materially differ.

A channel owns, when applicable:
- fulfilment mode;
- minimum-order value;
- fixed fulfilment/delivery fee;
- optional free-delivery threshold;
- commercial-condition observation timestamp;
- explicit validity interval when supplied by the source.

Travel cost to pickup locations is outside the MVP.

### Offer

A Fulfilment-Channel-specific commercial observation for one Product Card/SKU.

An Offer owns:
- Product Card/SKU;
- Fulfilment Channel;
- price amount and currency;
- availability state: `available`, `unavailable`, or `unknown`;
- observed-at timestamp;
- explicit valid-from/valid-until interval when supplied by the source.

Only an `available` Offer inside an explicit validity interval, when one exists, is executable.

When no explicit `valid_until` exists, the MVP does not invent an expiry. The observation remains usable as a budget estimate and retains its age/provenance; this is not a guarantee of current checkout price.

The same rule applies to channel-level conditions.

## Derived state

For comparison, package price and quantity may be normalized into comparable unit-cost measures. These are derived values; the observed Offer remains authoritative for the commercial terms.

For nutrition calculation, effective package nutrient quantities are derived from the effective per-100-g nutrient profile and executable edible quantity.

Purchase Planning derives a `Purchase Group` by grouping selected Offers from one Fulfilment Channel. Channel-level minimum order and delivery/fulfilment fee are evaluated once for that group.

## Invariants

- price belongs to an Offer, not to Base Food or SKU identity;
- package size belongs to the concrete Product Card/SKU;
- one SKU may have multiple Offers across Merchants/Fulfilment Channels;
- a nutritionally executable SKU has an explicit conversion from package quantity to edible grams;
- Product Card nutrient overrides take precedence over Base Food defaults only where a semantically identical normalized component is explicitly provided;
- unknown/trace override data do not silently erase known Base Food defaults unless the product establishes that the Base Food default is inapplicable;
- only `available` Offers satisfying explicit validity bounds are executable;
- absence of `valid_until` does not imply an invented expiration time;
- minimum-order and delivery/fulfilment fee semantics belong to a Fulfilment Channel and are applied once per Purchase Group;
- price currency is part of commercial identity; one executable plan does not mix currencies without an accepted FX policy;
- acquisition conditions may affect the economic value of an Offer independently of unit price.

## MVP data acquisition

Product Cards, Fulfilment Channels and Offers may be entered manually or imported. Automatic price/store synchronization is not required.

## Explicit exclusions

Inventory ownership, household stock, leftover carry-over, travel/transport cost between merchants, FX conversion, coupons, loyalty pricing, subscriptions and complex cross-offer promotions are outside the MVP.

## Material unknowns before architecture

None currently owned by Market Catalog.
