# User Journey Design — Frontend

Status: accepted for the frontend design target.

Owner: APPLICATION-DESIGN.

## J1 — Maintain household member profiles

**Actor:** local Nutrition Management user.

**Goal:** keep the household inputs required for target derivation current.

**Entry:** open Household workspace.

**Flow:**
1. inspect household members and current profile completeness;
2. choose either **Add member** or open an existing member;
3. enter/update date of birth, sex, height, current weight/date, PAL where applicable, and optional target weight/date;
4. submit;
5. for Add member, the application creates a provider-owned opaque Member identity together with the initial profile; for an existing member, it replaces that member's current profile;
6. system validates accepted profile invariants and persists source facts atomically for the selected operation;
7. UI returns to the member/household context and marks derived targets as recalculated-on-demand rather than editable stored truth.

**Alternate/recovery:**
- invalid source fact -> no mutation; field/summary rejection remains visible;
- PAL/source applicability not required or unresolved by accepted semantics -> do not invent defaults;
- persistence/technical failure -> no confirmed success.

## J2 — Maintain planning catalog facts

**Goal:** prepare enough Food Knowledge and Market Catalog data for an executable plan.

**Flow:**
1. inspect Base Foods and their category/nutrient/provenance facts;
2. create/update accepted manual Base Food facts when required;
3. inspect Product Cards/SKUs and executable edible quantity;
4. create/update Merchants/Fulfilment Channels and shared order conditions;
5. create/update Offers with price, currency, availability, observation and validity provenance;
6. system validates provider-owned semantics before committing each fact.

Bulk/reference imports remain available through existing import mechanisms and are not duplicated by this frontend slice.

**Important distinctions:**
- Base Food != SKU != Offer;
- package quantity != planned utilized quantity;
- unavailable/unknown offer != executable offer;
- missing explicit expiry != invented expiration.

## J3 — Generate purchase plan

**Goal:** obtain the best accepted executable 30-day household basket.

**Preconditions:**
- household/profile facts exist;
- accepted provider catalogs contain whatever data is available;
- user supplies explicit derivation date and market as-of.

**Flow:**
1. open Plan workspace;
2. select household;
3. enter derivation date and market as-of;
4. review readiness summary;
5. submit Generate Purchase Plan;
6. system derives target, captures one coherent provider snapshot, closes read scope, optimizes, recalculates reportable facts and optionally enriches gaps;
7. UI presents the accepted outcome.

**Outcomes:**
- `mapped_complete` -> executable plan plus separately visible unsupported coverage/safety caveats;
- `partial` -> executable best plan plus explicit gaps/indeterminate/variety shortfall;
- `no_executable_plan` -> no basket represented as successful;
- technical failure -> distinct retryable/non-domain failure.

## J4 — Interpret and act on plan result

**Goal:** understand what to buy, where, why, and what remains uncertain.

**Flow:**
1. inspect outcome summary and total acquisition cost;
2. inspect Purchase Groups by Fulfilment Channel;
3. inspect package count, purchased edible quantity, planned utilized quantity and surplus per line;
4. inspect nutrition/energy coverage;
5. inspect unsupported coverage separately from indeterminate evidence;
6. inspect variety assessment and safety diagnostics;
7. inspect theoretical Base Food gap suggestions where available;
8. inspect price/condition and nutrition provenance.

The frontend does not persist a saved plan merely because the result is displayed.

## J5 — Recover from changed inputs

When a profile, food, SKU, channel or offer is changed after a plan was shown, that prior page is historical browser content only.

The system does not claim the old result is current. The user generates a new plan with explicit dates/times to obtain a new accepted result.

## Journey boundary

These journeys intentionally do not decide route strings, visual layout, framework, component library or persistence mechanics.
