# ADR-006 — Commercial offers are scoped to fulfilment channels with explicit observation/validity semantics

Status: `accepted`.

Date: 2026-09-15.

## Context

Purchase Planning must calculate a real purchasable basket, including package counts, selected merchants, delivery costs and minimum-order conditions. Delivery and minimum-order rules usually apply to a group of items acquired through one store/channel, not independently to each SKU price.

The previous tactical baseline placed these conditions directly on Offer. That makes basket-global cost semantics ambiguous: the same delivery fee could be repeated across multiple lines, while minimum-order conditions couple multiple Offers.

Commercial observations also change independently of product identity. The MVP allows manual/imported market data and does not promise live synchronization, so temporal provenance and availability must be explicit without inventing an arbitrary freshness cutoff.

## Decision

### Merchant

`Merchant` is the seller identity.

### Fulfilment Channel

A `Fulfilment Channel` is a concrete acquisition context for one Merchant through which multiple SKU Offers can be purchased together under shared order conditions.

The MVP supports two fulfilment modes:

- `pickup` — acquisition from a concrete store/pickup context;
- `delivery` — remote order delivered to the household/customer context.

A Merchant may have multiple Fulfilment Channels when store/location or delivery-service conditions materially differ.

A Fulfilment Channel owns order-level commercial conditions, when applicable:

- fulfilment mode;
- minimum order value;
- fixed fulfilment/delivery fee;
- optional free-delivery threshold that waives the fixed fee;
- observed-at timestamp for the conditions;
- explicit valid-from/valid-until interval when supplied by the source.

Travel/transport cost to a pickup location remains outside the MVP.

### Offer

An `Offer` is a Merchant/Fulfilment-Channel-specific commercial observation for one Product Card/SKU.

An Offer owns:

- Product Card/SKU reference;
- Fulfilment Channel reference;
- price amount and currency;
- availability state;
- observed-at timestamp;
- explicit valid-from/valid-until interval when supplied by the source.

Availability states are:

- `available` — source evidence says the SKU can currently be acquired through the channel;
- `unavailable` — source evidence says it cannot currently be acquired;
- `unknown` — availability is not known reliably enough to make the line executable.

Only an `available` Offer that is inside its explicit validity interval, when such an interval exists, is executable for a Purchase Plan.

If a source provides no `valid_until`, the MVP does not invent one. The Offer remains usable as a price estimate based on its observation, and the Purchase Plan retains/exposes `observed_at`; this does not guarantee that checkout price still matches the observation.

The same principle applies to channel-level conditions without an explicit expiry.

### Currency

Price identity includes currency. No FX conversion policy is introduced in the MVP.

All selected Offers and order-level charges in one executable Purchase Plan must therefore use one compatible currency. Offers in another currency may remain market knowledge but cannot be mixed into that plan without a future accepted FX policy.

### Purchase group

Purchase Planning groups selected Offers by Fulfilment Channel. One such group is a `Purchase Group`.

For each Purchase Group:

- line prices are summed from selected package counts;
- the channel minimum-order condition is checked against the applicable merchandise subtotal;
- the channel fulfilment fee is applied once;
- the fee is waived when an applicable free-delivery threshold is reached;
- resulting acquisition cost contributes once to the plan total.

Offer price and channel conditions remain Market Catalog facts. Purchase Planning owns the derived grouping and resulting total cost.

### Unsupported conditions

Coupons, loyalty programs, personalized pricing, complex tiered delivery rules, subscriptions and cross-merchant promotions are outside the MVP unless they can already be represented by the simple fixed fee/minimum/free-threshold semantics above.

A commercial condition that cannot be represented reliably is not silently approximated. The affected channel/offer may remain catalog knowledge but is not treated as fully executable under unknown material cost conditions.

## Consequences

- delivery/minimum-order coupling has one semantic owner and is no longer duplicated across Offer lines;
- basket cost can be calculated deterministically per Purchase Group;
- price observations remain usable for budget estimation without an arbitrary global staleness duration;
- users can see how old a price/condition observation is rather than receiving a false freshness guarantee;
- live price synchronization remains unnecessary for MVP;
- Purchase Planning can compare merchants/channels globally while preserving source commercial facts;
- complex promotion engines and foreign-exchange policy remain outside scope.

## Alternatives considered

### Keep delivery/minimum-order fields on every Offer

Rejected because those conditions couple multiple selected lines and would create duplicated or inconsistent order-cost semantics.

### Expire every price automatically after a fixed number of days

Rejected because no accepted requirement or source semantics justify one universal freshness interval. Observation age should be explicit evidence; explicit source validity windows remain authoritative when present.

### Treat unknown availability as available

Rejected because that would turn missing market evidence into a claim that a purchase line is executable.

### Model every promotion/coupon rule in MVP

Rejected because it materially expands the commercial-rule model without being required for the first end-to-end budget calculation.

## Supersession

Supersedes: none.
Superseded by: none.
