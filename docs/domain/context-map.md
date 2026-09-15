# Nutrition Management Context Map

Status: `accepted`.

| Provider / owner | Consumer | Purpose | Published semantic contract | Time / unknown / provenance semantics |
|---|---|---|---|---|
| Nutrition Targeting | Purchase Planning | Supply the demand side of planning | Household 30-day nutrition target, with retained member-level derivation/provenance | MVP planning horizon is 30 days; active nutrition-standard version is part of provenance |
| Food Knowledge | Market Catalog | Provide the semantic base for concrete commercial products | Base food identity, default nutrient profile, category membership, nutrition-data provenance | Market data may override defaults at SKU level without changing base-food truth |
| Food Knowledge | Purchase Planning | Provide theoretical food alternatives and category semantics | Base foods, nutrient profiles, categories, provenance | Used especially when purchasable catalog cannot reasonably close a nutrient gap |
| Market Catalog | Purchase Planning | Supply what can actually be bought | SKU/product data, effective nutrient data, package size, merchant offers, price and fulfilment conditions | Offer price/conditions are commercial observations and may change independently of base food knowledge |

## Direction of authority

- Nutrition Targeting owns what the household needs nutritionally.
- Food Knowledge owns what a food means nutritionally in normalized form.
- Market Catalog owns what commercial goods and offers are available.
- Purchase Planning owns the decision about which concrete basket to recommend for the calculation period.

Consumers must not reinterpret provider-owned facts as their own canonical truth.

This map is semantic; it is not a service, database or deployment dependency diagram.
