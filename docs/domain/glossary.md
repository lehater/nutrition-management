# Ubiquitous Language

Status: `accepted` for the current MVP domain baseline.

| Term | Status | Meaning | Owner / scope |
|---|---|---|---|
| Nutrition Management | accepted | Product/system working name. | Whole product |
| Calculation Period | accepted | Period over which MVP needs, planning and cost are calculated; fixed to 30 days in MVP. | Whole product |
| Household | accepted | Calculation scope containing one or more Household Members. | Nutrition Targeting |
| Household Member | accepted | Person whose current profile contributes nutritional demand to the household target. | Nutrition Targeting |
| Nutrition Profile | accepted | Current member source facts and weight goal used to derive nutritional needs; date of birth is the authoritative age source and chronological age is derived at target-derivation time. | Nutrition Targeting |
| Nutrition Standard Set | accepted | Immutable-at-use, versioned composition of sourced nutrient references, safety limits and target-derivation policies; one version is active by default in MVP. | Nutrition Targeting |
| Nutrient Reference | accepted | Sourced adequacy/reference value preserving its semantic kind, applicability and native basis; it may resolve to a point, bound or interval. | Nutrition Targeting |
| Safety Limit | accepted | Sourced upper-safety semantic such as an EFSA UL or safe level; separate from the preferred/adequacy target. | Nutrition Targeting |
| Physical Activity Level (PAL) | accepted | Numeric multiplier representing physical activity for energy derivation under the active Nutrition Standard Set. | Nutrition Targeting |
| Member Nutrition Target | accepted | Rebuildable 30-day energy/nutrient target specification, with separate applicable safety limits and provenance, derived from one member profile and the active standards. | Nutrition Targeting |
| Household Nutrition Target | accepted | Aggregated compatible 30-day nutritional demand consumed by the MVP purchase optimizer; it does not guarantee member-level safety or allocation feasibility. | Nutrition Targeting |
| Canonical Nutrient Component | accepted | Food-composition nutrient identity based on the BLS 4.0 component vocabulary, with component-specific canonical unit and semantics. | Food Knowledge |
| Nutrient Measure | accepted | Quantitative nutrient meaning used for comparison; either one canonical component or an explicit derived expression over compatible components. | Food Knowledge / Nutrition Targeting cross-context contract |
| Base Food | accepted | Normalized theoretical food with nutrient profile and category semantics, independent of a concrete commercial SKU. | Food Knowledge |
| Food Category | accepted | Hierarchical variety classification with a controlled DGE-aligned MVP top-level set plus `other_or_composite`; each Base Food has one primary top-level category. | Food Knowledge |
| Materially Represented | accepted | A Base Food/category contributes at least 1% of total planned utilized edible mass or 1% of total planned food energy and therefore counts toward MVP variety assessment. | Food Knowledge / Purchase Planning contract |
| Nutrition Data Source | accepted | Provenance metadata for nutritional data, including source name and optional URL/version/date; nutrient-level provenance is retained where available. | Food Knowledge |
| Product Card / SKU | accepted | Concrete commercial food product based on a Base Food, with package data, edible-quantity conversion when required, and optional nutrient overrides. | Market Catalog |
| Edible Quantity | accepted | Quantity of edible food represented by one package, resolved to grams for quantitative nutrition calculation. | Market Catalog |
| Effective Nutrient Profile | accepted | Derived SKU nutrient profile formed from Base Food defaults plus semantically identical normalized SKU overrides. | Market Catalog |
| Merchant | accepted | Seller identity relevant to acquisition planning. | Market Catalog |
| Fulfilment Channel | accepted | Concrete pickup or delivery acquisition context for one Merchant, owning shared order-level conditions for multiple Offers. | Market Catalog |
| Offer | accepted | Channel-specific commercial observation for one SKU, including price/currency, availability, observation time and explicit validity when known. | Market Catalog |
| Purchased Edible Quantity | accepted | Edible amount obtained by buying the integer package count for a Purchase Plan line. | Purchase Planning |
| Planned Utilized Quantity | accepted | Portion of purchased edible quantity assigned to the 30-day basket for nutritional coverage and variety calculation; it is planning state, not actual-consumption tracking. | Purchase Planning |
| Package Surplus | accepted | Purchased edible quantity minus planned utilized quantity; it affects acquisition cost but does not count as planned nutrition/variety and does not create MVP inventory state. | Purchase Planning |
| Purchase Group | accepted | Set of selected Offer lines acquired through one Fulfilment Channel, to which shared minimum-order and fulfilment-fee conditions are applied once. | Purchase Planning |
| Purchase Plan | accepted | Primary recommended 30-day basket of executable SKUs/offers with integer package quantities, planned utilized quantities, Purchase Groups, total cost and mapped nutritional/variety assessment. | Purchase Planning |
| Mapped Complete | accepted | Purchase Plan outcome where all active target references with accepted food-side mappings are determinate and satisfied under the MVP policy and the variety target is met; it is not a claim of complete nutrition or member-level safety. | Purchase Planning |
| Partial Purchase Plan | accepted | Best executable plan when at least one mapped target is violated/indeterminate or the variety target cannot be met; gaps and uncertainty remain explicit. | Purchase Planning |
