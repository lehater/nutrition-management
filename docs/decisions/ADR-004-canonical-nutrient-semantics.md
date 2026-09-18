# ADR-004 — MVP canonical nutrient semantics use BLS 4.0 component vocabulary

Status: `accepted`.

Date: 2026-09-15.

## Context

Nutrition Targeting expresses what nutrients the household needs, while Food Knowledge expresses what nutrients foods contain. Purchase Planning can compare the two only if nutrient identity, expression/form, unit and food-composition basis are semantically compatible.

String names are insufficient. Examples such as vitamin A in retinol activity equivalents versus retinol equivalents, niacin versus niacin equivalents, folate versus folate equivalents, sodium versus salt, and EPA+DHA versus total omega-3 demonstrate that similarly named values are not interchangeable.

The Max Rubner-Institut Bundeslebensmittelschlüssel (BLS) 4.0 is Germany's current national nutrient database. It provides EuroFIR-aligned component codes, component-specific units, documented formulas, per-value provenance and a uniform food-composition basis of 100 g edible portion.

## Decision

### Canonical food-composition vocabulary

For the MVP, Food Knowledge uses BLS 4.0 nutrient component codes and semantics as the canonical vocabulary for food-composition components.

The project does not infer nutrient identity from display names. A source value can be normalized to a canonical component only when its semantic meaning is compatible with that component.

Examples:

- energy for planning uses `ENERCC` in kcal;
- protein uses `PROT625`;
- available carbohydrate uses `CHO`;
- total fat uses `FAT`;
- total fibre uses `FIBT`;
- vitamin A in RAE uses `VITAA`, not `VITA`;
- niacin equivalents use `NIAEQ`, not plain `NIA`;
- folate equivalents use `FOL`, not plain food folate `FOLFD`;
- sodium `NA` and salt `NACL` are distinct nutrient components even though BLS defines a formula relationship between them.

### Canonical food-composition basis

A normalized Food Knowledge nutrient profile is expressed per `100 g edible portion`, matching BLS 4.0 semantics.

Source values using another food basis may enter the canonical profile only after an explicit, semantically justified conversion to edible mass. A missing conversion is not guessed.

### Canonical quantity unit

Each canonical nutrient component retains its BLS-defined unit (`g`, `mg`, `µg`, or `kcal` for the selected energy component). Unit conversion may rescale a quantity only within the same semantic component.

Generic exact scaling is allowed for compatible mass units (`g`, `mg`, `µg`) and energy units (`1 kcal = 4.184 kJ`).

Transformations between different nutrient components are not unit conversions. They require an accepted nutrient formula or crosswalk, for example BLS `NACL = NA × 2.5` or `VITAA = RETOL + 1/12 × CARTB + 1/24 × CAROTPAXB`.

### Derived nutrient measures

A Nutrition Standard may target a measure that is not one BLS component. The MVP therefore permits a versioned derived Nutrient Measure defined as an explicit expression over canonical components with compatible units.

Example:

`EPA_DHA = F20:5CN3 + F22:6CN3`.

Derived measures are semantic definitions, not ad-hoc optimizer formulas.

### Cross-context mapping

A Nutrition Targeting reference becomes comparable with Food Knowledge only through an accepted mapping to either:

- one canonical BLS component; or
- one explicitly defined derived Nutrient Measure.

The mapping retains the source reference identity and the food-side component/measure identity. Similar names alone never establish equivalence.

A reference without an accepted mapping may remain visible as source nutrition knowledge but cannot be claimed as quantitatively covered by Purchase Planning.

### Unknown, trace and zero

Food Knowledge preserves the distinction between:

- numeric known amount;
- known/logical zero;
- trace/present but not quantitatively known;
- missing/unknown value.

Missing or trace data are not silently converted to zero. A plan cannot claim deterministic coverage from a nutrient amount that is quantitatively unknown.

### Precision and rounding

Source precision is retained as provenance. Normalization and derived-measure calculation do not introduce semantic intermediate rounding.

Rounding is a presentation/export concern unless a source standard explicitly defines a rounding rule. Purchase Planning scoring tolerances are separate optimization policy and must not mutate canonical nutrient values.

### Product/SKU normalization consequence

Because Base Food defaults and SKU overrides are merged component-by-component, a Product Card nutrient override must be normalized to the same canonical component, unit and `100 g edible portion` basis before it can override the Base Food value.

An executable SKU must provide enough quantity semantics to convert purchased package quantity to edible grams. A volume- or count-based package therefore needs an accepted mass-equivalent conversion (for example density, edible unit mass, or explicit edible package mass). If that conversion is unavailable, the SKU may remain catalog knowledge but cannot participate in quantitative nutrition optimization.

## Consequences

- BLS 4.0 becomes the MVP semantic anchor for Food Knowledge nutrient composition, not merely one optional import source.
- BLS component codes are versioned external semantic identifiers; a later BLS vocabulary change is adopted explicitly rather than silently remapped.
- DGE/ÖGE target references are crosswalked by meaning, expression/form and unit, not by text label.
- The active optimizer-controlled nutrient set is the intersection of active Nutrition Standard references and Food Knowledge components/derived measures with accepted mappings.
- Missing composition data produces uncertainty rather than false zero contribution.
- Product labels expressed per 100 ml or per serving require an explicit conversion before partial override of a per-100-g Base Food profile.
- Package normalization must expose edible-mass equivalence when package units are not already mass-based.

## Alternatives considered

### Define an independent project-wide nutrient enum from scratch

Rejected for MVP because it would duplicate a maintained national/EuroFIR-aligned vocabulary and create unnecessary mapping work without product-specific semantic benefit.

### Match nutrients by display name

Rejected because names hide materially different expressions and forms such as RE versus RAE, niacin versus niacin equivalents and sodium versus salt.

### Normalize every nutrient amount to grams

Rejected because unit scaling does not erase nutrient identity or expression semantics and would make source values harder to audit. Component-native canonical units remain clearer while still allowing exact compatible-unit conversion.

### Allow both per-100-g and per-100-ml canonical profiles

Rejected for the MVP because component-wise fallback/override across different food bases becomes ambiguous. One edible-mass basis keeps Base Food/SKU composition merge semantics deterministic.

## Supersession

Supersedes: none.
Superseded by: [`ADR-013`](ADR-013-limit-qualified-nutrient-evidence.md) for the four-state-only nutrient-evidence scope.
