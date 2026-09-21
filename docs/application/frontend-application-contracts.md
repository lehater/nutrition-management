# Frontend Application Contracts

Status: accepted for the frontend design target.

Owner: APPLICATION-DESIGN.

## Purpose

Expose the smallest application-facing read/command surface required by the accepted frontend journeys without allowing the web adapter to query persistence or recreate domain policy.

These contracts are semantic application contracts. Python function/class shape remains implementation freedom.

## Common outcome rules

Every command/query has one of:
- accepted result;
- accepted validation/not-found conflict as applicable;
- technical application failure.

A transport/web status is never part of the contract.

Opaque provider identifiers remain opaque outside their owning context.

## Nutrition Targeting

### ListHouseholds

Returns existing household references derivable from provider-owned state plus member count.

The first frontend slice does not introduce an independently editable empty-household aggregate. Initial household/profile state may still be established through existing import/setup mechanisms.

### ListMemberProfiles(household_id)

Returns current source-profile summaries for the household.

### GetMemberProfile(household_id, member_id)

Returns the current accepted source facts required by the member editor.

### CreateMember(household_id, profile)

Creates one new Household Member identity and its initial current Nutrition Profile atomically through Nutrition Targeting application/domain validation.

Semantics:
- Nutrition Targeting generates/owns the new opaque `member_id`; the frontend never manufactures it;
- success returns the created `member_id` plus the accepted current profile summary;
- invalid profile input creates neither Member identity nor profile state;
- technical failure is not reported as confirmed creation;
- duplicate submission handling must not silently create two members; if idempotent creation is required by the selected adapter, that adapter/application contract must make its idempotency key/semantics explicit rather than inferring identity from profile fields.

### SaveMemberProfile(household_id, member_id, profile)

Replaces the one current profile for an already existing member through Nutrition Targeting validation. It does not create Member identity implicitly.

The command may reuse/refine the existing profile-import application command, but the web adapter must not call the repository directly.

### GetActiveStandardSummary()

Returns:
- active standard version;
- source/provenance label sufficient for UI display.

It does not return persistence representation and does not make target reference rows editable.

## Food Knowledge

### ListBaseFoods()

Returns presentation-neutral summaries:
- Base Food id;
- name;
- category;
- provenance summary.

### GetBaseFood(base_food_id)

Returns canonical Food Knowledge facts required for detail/edit presentation, including nutrient evidence states.

### SaveManualBaseFood(food)

Accepts canonical/manual Food Knowledge input and validates through Food Knowledge application/domain semantics before persistence.

It may reuse/refine the existing food-import command. Non-quantitative evidence is never coerced into numeric zero.

Bulk/source-specific imports remain separate provider application commands.

## Market Catalog

### ListProducts() / GetProduct(sku_id) / SaveProduct(product)

Expose Product Card/SKU facts required by the UI while preserving Base Food reference and executable-edible-quantity semantics.

### ListChannels() / GetChannel(channel_id) / SaveChannel(channel)

Expose Merchant/Fulfilment Channel facts and order-level conditions.

### ListOffers() / GetOffer(offer_id) / SaveOffer(offer)

Expose Offer price/currency/availability/observation/validity facts.

Save commands may reuse/refine existing import commands; the web adapter never writes Market Catalog repositories directly.

## Purchase Planning

### GeneratePurchasePlan

Reuse the already accepted contract:

`GeneratePurchasePlan(household_id, derivation_date, market_as_of)`.

The frontend consumes the accepted Purchase Plan result and does not add a second planning/query model.

## Query sizing

The first local MVP may materialize provider collections for server-side presentation filtering where practical.

If measured data volume requires bounded paging/query contracts, add those to the owning provider application contract. The frontend must not invent database-specific paging/query semantics.

## Prohibited application shortcuts

- generic cross-context CRUD service;
- web adapter owning repository transactions;
- returning SQLAlchemy rows/models as contracts;
- frontend-specific duplicate domain models;
- one global search/query service spanning bounded contexts;
- presentation code selecting active standard or interpreting offer executability.

## Implementation challenge criterion

A frontend route is implementation-ready only when its required contract above exists or is implemented behind an equivalent accepted provider-owned application contract.

Missing contract shape is an APPLICATION-DESIGN gap, not permission for the web adapter to reach into infrastructure.
