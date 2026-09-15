# Canonical Nutrient Semantics

Status: `accepted` for the current MVP tactical baseline.
Lifecycle layer: `S2 Domain Semantics / Tactical DDD`.
Owners: `Food Knowledge` for canonical food-composition components; `Nutrition Targeting` for target-reference-to-component mappings.

## Purpose

Define the semantic contract that allows Nutrition Targeting quantities to be compared with Food Knowledge quantities without conflating names, units, chemical forms, equivalent expressions or food-composition bases.

The governing decision is [`ADR-004`](../decisions/ADR-004-canonical-nutrient-semantics.md).

## Canonical component vocabulary

The MVP canonical food-composition vocabulary is based on BLS 4.0 nutrient component codes and definitions.

A canonical component has:
- BLS component code;
- semantic nutrient/component meaning;
- canonical unit defined by BLS;
- source/version provenance for the vocabulary definition.

The code is not merely a display alias. `VITAA`, `VITA`, `RETOL`, `NA` and `NACL`, for example, represent different measurable semantics and are not interchangeable.

## Canonical food-composition basis

Food Knowledge normalized nutrient profiles express component quantities per:

`100 g edible portion`.

The edible-portion basis is part of the quantity meaning. A numeric amount without its food basis is incomplete composition data.

## Canonical units

For one canonical component, quantities may be rescaled among compatible units before entering the canonical form.

Accepted generic exact conversions:
- `1 g = 1000 mg`;
- `1 mg = 1000 µg`;
- `1 kcal = 4.184 kJ`.

The canonical stored/published unit for a component remains the BLS 4.0 component unit. `ENERCC` is the canonical energy component used for MVP nutrition comparison and is expressed in kcal.

A transformation between different components is a nutrient formula, not a generic unit conversion.

## Nutrient formulas and derived measures

BLS-defined calculated components retain their BLS formulas and semantics. Examples include:

- `VITAA = RETOL + 1/12 × CARTB + 1/24 × CAROTPAXB`;
- `FOL = FOLFD + 1.7 × FOLAC`;
- `NIAEQ = NIA + TRP × 1000 / 60`;
- `NACL = NA × 2.5`.

A target measure not represented by one canonical BLS component may be defined as an explicit project Nutrient Measure over compatible canonical components.

Initial project-derived measure required by the active DGE/ÖGE reference set:

- `EPA_DHA = F20:5CN3 + F22:6CN3`.

A derived measure owns a stable semantic formula. Purchase Planning consumes it; it does not recreate or reinterpret that formula privately.

## Reference-to-composition crosswalk

A Nutrition Targeting reference is quantitatively comparable with food composition only after an accepted semantic crosswalk exists.

The crosswalk checks:
- nutrient/component identity;
- expression or equivalent basis;
- chemical/form scope where material;
- unit compatibility;
- whether a source value is a primitive component or a defined derived measure.

Examples of accepted mappings for `mvp-v1`:

| Nutrition reference meaning | Food-side component/measure | Canonical unit | Note |
|---|---|---|---|
| Energy | `ENERCC` | kcal | `kJ` source values may be exactly converted |
| Protein | `PROT625` | g | BLS protein Nx6.25 semantics |
| Available carbohydrate | `CHO` | g | not total carbohydrate by arbitrary label naming |
| Total fat | `FAT` | g |  |
| Total fibre | `FIBT` | g |  |
| Saturated fatty acids | `FASAT` | g |  |
| Monounsaturated fatty acids | `FAMS` | g |  |
| Polyunsaturated fatty acids | `FAPU` | g |  |
| Linoleic acid | `F18:2CN6` | g |  |
| Alpha-linolenic acid | `F18:3CN3` | g |  |
| EPA + DHA | `EPA_DHA` | g | project-derived measure |
| Vitamin A, RAE | `VITAA` | µg | do not map to `VITA`/RE |
| Vitamin D | `VITD` | µg | BLS sum semantics apply |
| Vitamin E, alpha-tocopherol | `VITE` | mg | BLS defines `VITE = TOCPHA` |
| Vitamin K | `VITK` | µg | BLS aggregate component |
| Thiamin | `THIA` | mg |  |
| Riboflavin | `RIBF` | mg |  |
| Niacin equivalents | `NIAEQ` | mg | do not map to plain `NIA` |
| Pantothenic acid | `PANTAC` | mg |  |
| Vitamin B6 | `VITB6` | µg | DGE values in mg are rescaled, not renamed |
| Biotin | `BIOT` | µg |  |
| Folate equivalents | `FOL` | µg | do not map to plain food folate `FOLFD` |
| Vitamin B12 | `VITB12` | µg |  |
| Vitamin C | `VITC` | mg |  |
| Sodium | `NA` | mg | salt is a different component |
| Chloride | `CLD` | mg |  |
| Potassium | `K` | mg |  |
| Calcium | `CA` | mg |  |
| Magnesium | `MG` | mg |  |
| Phosphorus | `P` | mg |  |
| Iron | `FE` | mg |  |
| Zinc | `ZN` | mg |  |
| Copper | `CU` | µg |  |
| Manganese | `MN` | µg |  |
| Fluoride | `FD` | µg |  |
| Chromium | `CR` | µg |  |
| Molybdenum | `MO` | µg |  |

A reference whose exact food-side semantics are not represented by an accepted mapping remains unsupported for deterministic coverage. The source reference itself remains available and is not silently dropped or approximated by a similarly named component.

## Safety-limit compatibility

Safety limits may have a narrower chemical/form scope than adequacy targets or BLS aggregate components.

A Safety Limit is quantitatively enforceable only when its scoped substance/form can be mapped to canonical Food Knowledge data at equal or finer semantic specificity.

Examples such as nicotinic acid versus nicotinamide must not be checked against aggregate niacin equivalents unless an accepted formula and sufficient component data establish that comparison.

An unmappable Safety Limit remains provenance/diagnostic information rather than a false hard constraint.

## Food nutrient value state

A nutrient data point has one of these semantic states:

- `known numeric` — a quantified amount is available;
- `known zero` — zero is supported by source evidence/logic;
- `trace` — the component is present but a reliable numeric amount is unavailable;
- `unknown` — no reliable value is available.

`trace` and `unknown` are distinct from zero.

For deterministic nutrition coverage, only known numeric values and known zero values provide exact arithmetic evidence. Unquantified trace/unknown values remain uncertainty and cannot prove target satisfaction.

## Provenance

Nutrient provenance is retained per data point when the source provides it, not merely once for the whole food.

For BLS 4.0 imports this includes, where available:
- BLS food identity/version;
- component code;
- value;
- value-origin category;
- concrete source/reference.

A derived component additionally identifies the formula/version used.

## Precision and rounding

Source numeric precision is preserved as source evidence.

Domain calculations:
- perform compatible-unit conversion before comparison;
- apply accepted nutrient formulas without intentional intermediate rounding;
- keep the normalized numeric result at calculation precision;
- round only for human-facing presentation/export unless an upstream source explicitly mandates a rounding rule.

Optimization tolerances do not rewrite nutrient quantities. They belong to Purchase Planning policy.

## Product Card overrides

A Product Card nutrient override can replace one Base Food component only after normalization to:
- the same canonical component/measure semantics;
- the same canonical component unit;
- the same `100 g edible portion` basis.

A label value expressed per 100 ml, per serving or per package is source evidence until the Product Card has enough quantity/conversion data to normalize it to the canonical edible-mass basis.

Missing override values continue to fall back to Base Food values only component-by-component. An unknown override is not an instruction to erase a known Base Food default unless the product explicitly establishes that the Base Food default is inapplicable.

## Executable package quantity

For a Product Card to participate in quantitative nutrition optimization, purchased package quantity must resolve to edible grams.

Direct mass packages can provide edible grams directly. Volume/count packages require an accepted conversion such as:
- explicit edible package mass;
- density for volume-to-mass conversion;
- edible unit mass for count-to-mass conversion.

If the conversion is missing, the Product Card may exist in Market Catalog but is not nutritionally executable in Purchase Planning.

## Invariants

- nutrient identity is semantic and is never inferred from display-name equality;
- one canonical component has one BLS-defined canonical unit in the MVP vocabulary;
- food composition is normalized per 100 g edible portion;
- generic unit conversion never changes nutrient identity;
- equivalent/aggregate transformations require an accepted nutrient formula;
- missing and trace values are never silently treated as zero;
- target coverage is claimed only for accepted target-to-composition mappings;
- Product Card fallback/override occurs only between semantically identical normalized components;
- intermediate calculation rounding does not mutate canonical nutrient truth.
