# Product Requirements

Status: `accepted`.
Lifecycle layer: `S1 Requirements`.

The system is advisory: it calculates, compares and explains practical nutrition plans rather than enforcing hard dietary constraints.

## Required capabilities

The system must support:
- deriving a person's applicable energy, macro- and micronutrient needs from known inputs and goals;
- planning what should be eaten over a chosen planning horizon;
- evaluating how well a plan covers nutritional needs over relevant reporting horizons;
- accounting for food and prepared portions already available;
- identifying nutritional and inventory gaps that affect the next purchase;
- producing a purchase plan for the chosen horizon;
- representing product prices in the context of seller, purchase method and other material acquisition conditions;
- comparing purchasing alternatives including delivery and pickup when data is available;
- calculating the cost of a candidate nutrition plan and estimating the budget required to reasonably cover nutritional needs;
- planning preparation, portioning and storage when relevant to the chosen plan;
- presenting multiple reasonable alternatives and their trade-offs rather than assuming one universal mathematical optimum.

## Evaluation dimensions

Candidate plans may be compared by:
- nutritional adequacy;
- energy fit;
- total cost;
- variety;
- unnecessary purchases or surplus;
- preparation frequency and effort;
- storage and operational convenience.

These dimensions are decision criteria, not universal hard constraints. Different goal profiles may change their relative importance.

## Initial scope boundaries

The initial scope does not require:
- therapeutic or disease-specific diets;
- weight-loss or weight-gain optimization;
- detailed actual-consumption logging;
- calorie-tracker workflows;
- proof that the user actually consumed the planned food.

Planned consumption is treated as actual consumption by default until adherence tracking becomes an explicit requirement.
