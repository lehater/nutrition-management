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

For nutrition calculation, effective package nutrient quantities are derived from the effective per-100-g nutrient profile and executable edible quantity.

## Invariants

- price belongs to an Offer, not to Base Food or SKU identity;
- package size belongs to the concrete Product Card/SKU;
- one SKU may be sold by multiple merchants at different prices;
- a nutritionally executable SKU has an explicit conversion from package quantity to edible grams;
- Product Card nutrient overrides take precedence over Base Food defaults only where a semantically identical normalized component is explicitly provided;
- unknown/trace override data do not silently erase known Base Food defaults unless the product establishes that the Base Food default is inapplicable;
- acquisition conditions may affect the economic value of an Offer independently of unit price.

## MVP data acquisition

Product Cards and Offers may be entered manually or imported. Automatic price/store synchronization is not required.

## Explicit exclusions

Inventory ownership, household stock, leftover carry-over and travel/transport cost between merchants are outside the MVP.

## Material unknowns before architecture

- exact representation of fulfilment methods and merchant-level order conditions;
- price/offer validity semantics and timestamps.
