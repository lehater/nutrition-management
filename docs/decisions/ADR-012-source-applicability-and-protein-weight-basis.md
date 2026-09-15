# ADR-012 — Source reference applicability is explicit and unresolved factors remain unsupported

Status: `accepted`.

Date: 2026-09-15.
Lifecycle owner: `S2 Tactical Domain Design / Nutrition Targeting`.

## Context

Preparing the sourced `mvp-v1` Nutrition Standard Set exposed reference applicability that cannot be reduced to age and sex without inventing product defaults.

Current DGE source semantics include, among other cases:

- adult zinc recommendations that vary by low, medium or high phytate intake;
- female iron rows whose applicable value may depend on menstruation or pre-/postmenopausal state rather than age alone;
- adult protein values expressed per kg body weight that are defined for normal weight and require a normal/reference weight for overweight adults.

The MVP Nutrition Profile deliberately does not own phytate-intake class, menstruation state or menopause state. Adding those inputs solely to make every external source row selectable would broaden the product profile without an accepted user need. Choosing defaults or inferring them from age would create unsupported nutrition claims.

ADR-003 already requires source-native applicability and source-owned relative bases. This ADR makes the unresolved-applicability behavior and the adult protein weight rule explicit.

Official source anchors:

- DGE zinc reference and FAQ: <https://www.dge.de/wissenschaft/referenzwerte/zink/> and <https://www.dge.de/gesunde-ernaehrung/faq/ausgewaehlte-fragen-und-antworten-zu-zink/>;
- DGE iron reference: <https://www.dge.de/wissenschaft/referenzwerte/eisen/>;
- DGE protein reference and FAQ: <https://www.dge.de/wissenschaft/referenzwerte/protein/> and <https://www.dge.de/gesunde-ernaehrung/faq/ausgewaehlte-fragen-und-antworten-zu-protein-und-unentbehrlichen-aminosaeuren/>.

## Decision

### Reference families and source variants

A nutrient reference concept is represented as a **reference family** containing one or more sourced variant rows. Each variant preserves its own value, source semantic kind, native basis/unit, applicability predicates and row provenance.

A selector may resolve a family to a quantitative Member Nutrition Target reference only when all applicability dimensions required to choose the source variant are known from accepted MVP profile facts or deterministic `mvp-v1` policy.

For one member and derivation date:

- exactly one matching selectable variant -> `resolved`;
- a potentially applicable family requires a source factor that the MVP does not own -> `unsupported_applicability`;
- known member facts place the member outside the general source reference's applicability -> `source_inapplicable`;
- source rows explicitly outside accepted MVP scope, such as pregnancy/lactation rows, remain `outside_mvp_scope` source provenance and are not active target gaps;
- more than one matching variant after all required applicability facts are known is an invalid Standard Set/data condition and must fail validation rather than choose arbitrarily.

`unsupported_applicability` records at least the reference family, missing applicability dimension(s), candidate source-row identities and standard-set/source provenance. It is not converted to zero and is not silently omitted.

The MVP does not introduce defaults for phytate intake, menstruation or menopause and does not infer those states from age.

### Zinc

For adults, `mvp-v1` retains the DGE low-, medium- and high-phytate zinc variants. Because the current Nutrition Profile does not own a phytate-intake class, adult zinc automatic target selection is `unsupported_applicability`.

Age groups for which DGE zinc applicability does not require phytate class remain selectable from the facts already owned by the profile.

### Iron

`mvp-v1` retains the DGE iron variants and their source notes for menstruating/non-menstruating and pre-/postmenopausal applicability.

When a female source family cannot be uniquely selected from current MVP facts because menstruation or menopause state is required, automatic iron target selection is `unsupported_applicability`. The system does not assume menstruation, non-menstruation, premenopause or postmenopause from chronological age.

Rows whose applicability is fully determined by accepted MVP facts remain selectable normally.

### Adult protein applicable weight

For adult DGE protein references expressed in `g/kg body weight/day`, `mvp-v1` computes BMI from current observed weight and height at derivation time and applies this rule:

- `18.5 <= BMI < 25.0`: `applicable_weight_kg = current_weight_kg`;
- `25.0 <= BMI < 30.0`: `applicable_weight_kg = 22 × height_m²`, matching the DGE adult reference-weight basis of BMI `22 kg/m²`;
- `BMI < 18.5` or `BMI >= 30.0`: the general DGE protein reference is `source_inapplicable` for automatic MVP derivation; no specialty-society or therapeutic substitute is introduced.

The current-weight observation date remains provenance and must satisfy the existing `current_weight_date <= derivation_date` invariant. The reference-weight calculation changes only the source basis used for protein derivation; it does not overwrite the member's current weight or become a target-weight goal.

### Propagation to household planning

Member Nutrition Target provenance preserves unresolved active reference families as applicability gaps. Household Nutrition Target carries those member-level gaps forward.

Purchase Planning treats active `unsupported_applicability` and `source_inapplicable` gaps as **unsupported coverage**, alongside unresolved target-to-food mappings. They are excluded from quantitative optimization because no valid numeric target exists, but remain visible in the plan result.

`mapped_complete` continues to mean complete only for the resolved, mapped subset. It must never imply that unsupported applicability gaps were satisfied.

## Consequences

- The production Standard Set can retain complete sourced variants without expanding the MVP profile merely to force row selection.
- Zinc and relevant female iron targets may remain quantitatively unsupported for some members; this is an explicit limitation rather than a fabricated target.
- Adult protein derivation gets a deterministic source-aligned applicable-weight rule using already-owned height and current-weight facts.
- Standard-set data needs stable reference-family identity in addition to row identity and explicit applicability dimensions.
- Member/Household target contracts and downstream reporting need an explicit unsupported-applicability representation.
- S3 topology does not need to reopen: these semantics remain owned by Nutrition Targeting and flow through its existing published target contract.

## Alternatives considered

### Add phytate, menstruation and menopause fields to the MVP profile now

Rejected because the current product requirements do not justify collecting these extra applicability facts, and doing so solely for source-table completeness would broaden profile scope unnecessarily.

### Pick medium phytate by default

Rejected because DGE publishes distinct adult values based on phytate exposure; selecting one without evidence would invent product policy.

### Infer menstruation or menopause from age

Rejected because the source itself distinguishes states that are not deterministically implied by age.

### Multiply all adult protein g/kg values by current observed weight

Rejected because DGE explicitly limits the g/kg reference to normal weight and uses normal/reference weight for overweight adults.

### Use BMI-22 reference weight for every adult

Rejected because this would discard the source's normal-weight body-weight-relative semantics and unnecessarily replace observed weight for members already within normal BMI.

## Supersession

This ADR refines the applicability and relative-weight details of ADR-003 without superseding its standard-set/source choices.

Supersedes: none.
Superseded by: none.
