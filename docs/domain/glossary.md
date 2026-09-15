# Ubiquitous Language

Status: `accepted` for the current MVP domain baseline.

| Term | Status | Meaning | Owner / scope |
|---|---|---|---|
| Nutrition Management | accepted | Product/system working name. | Whole product |
| Calculation Period | accepted | Period over which MVP needs, planning and cost are calculated; fixed to 30 days in MVP. | Whole product |
| Household | accepted | Calculation scope containing one or more Household Members. | Nutrition Targeting |
| Household Member | accepted | Person whose current profile contributes nutritional demand to the household target. | Nutrition Targeting |
| Nutrition Profile | accepted | Current member source parameters and weight goal used to derive nutritional needs. | Nutrition Targeting |
| Nutrition Standard Set | accepted | Versioned, sourced rules/reference values used to derive target nutrient ranges; one version is active in MVP. | Nutrition Targeting |
| Member Nutrition Target | accepted | Rebuildable 30-day nutrient target ranges derived from one member profile and the active standards. | Nutrition Targeting |
| Household Nutrition Target | accepted | Aggregated 30-day target ranges consumed by the MVP purchase optimizer. | Nutrition Targeting |
| Base Food | accepted | Normalized theoretical food with nutrient profile and category semantics, independent of a concrete commercial SKU. | Food Knowledge |
| Food Category | accepted | Hierarchical classification used for variety rules; top-level categories are controlled and subcategories extensible. | Food Knowledge |
| Nutrition Data Source | accepted | Provenance metadata for nutritional data, including source name and optional URL/version/date. | Food Knowledge |
| Product Card / SKU | accepted | Concrete commercial food product based on a Base Food, with package data and optional nutrient overrides. | Market Catalog |
| Effective Nutrient Profile | accepted | Derived SKU nutrient profile formed from Base Food defaults plus explicitly supplied SKU overrides. | Market Catalog |
| Merchant | accepted | Seller/store identity relevant to acquisition planning. | Market Catalog |
| Offer | accepted | Merchant-specific commercial terms for purchasing an SKU, including price and relevant fulfilment conditions. | Market Catalog |
| Purchase Plan | accepted | Recommended 30-day basket of concrete SKUs/offers, package quantities, merchants, total cost and nutritional/variety assessment. | Purchase Planning |
