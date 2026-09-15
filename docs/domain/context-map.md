# Nutrition Management Context Map

Status: `accepted`.

| Provider / owner | Consumer | Purpose | Published semantic contract | Time / unknown / provenance semantics |
|---|---|---|---|---|
| Nutrition Targeting | Purchase Planning | Supply the demand side of planning | Household 30-day nutrition target with typed references, accepted food-side mappings, retained member-level derivation/provenance and separate member Safety Limits | MVP planning horizon is 30 days; active Nutrition Standard Set version and derivation date are provenance; unsupported mappings remain explicit |
| Food Knowledge | Market Catalog | Provide the semantic base for concrete commercial products | Base Food identity, canonical BLS-based nutrient profile per 100 g edible portion, derived Nutrient Measures, category membership and nutrition-data provenance | Market data may override defaults only after normalization to semantically identical nutrient component/unit/basis; unknown/trace values remain distinct from zero |
| Food Knowledge | Purchase Planning | Provide theoretical food alternatives and variety semantics | Base Foods, canonical nutrient profiles/measures, controlled Food Categories, material-representation semantics and provenance | Used for mapped coverage, variety evaluation and theoretical gap-closing suggestions; source/unknown evidence is preserved |
| Market Catalog | Purchase Planning | Supply what can actually be bought | executable Product Cards/SKUs, edible package quantities, Merchants, Fulfilment Channels, Offers, price/availability/validity and order-level conditions | commercial observations carry observed-at/explicit validity provenance; unknown availability is not executable; channel conditions couple lines in one Purchase Group |

## Direction of authority

- Nutrition Targeting owns what the household needs nutritionally and the semantic mapping from active references to food-side Nutrient Measures.
- Food Knowledge owns what a food means nutritionally in normalized form and how it is categorized for variety.
- Market Catalog owns what commercial goods/channels/offers are available and their observed commercial conditions.
- Purchase Planning owns the decision about which executable basket to recommend, the Purchase Groups it forms and the resulting coverage/variety/cost assessment.

Consumers must not reinterpret provider-owned facts as their own canonical truth.

This map is semantic; it is not a service, database or deployment dependency diagram.
