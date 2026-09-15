# Problem / Evidence

Status: `accepted`.
Lifecycle layer: `S0 Problem / Evidence`.

## Problem

A household with several members can have materially different nutritional needs because of age, sex, body size, physical activity and weight goals. The practical problem is to determine what food should be purchased for a calculation period so that the household's combined nutritional needs are reasonably covered without unnecessary spending or ad-hoc purchases.

The user also needs to understand the budget required to achieve that nutritional coverage and where concrete purchasable goods should be bought at the best overall acquisition cost.

## Initial target situation

The MVP targets a household with one or more members and a single calculation horizon of 30 days.

Each member has one current nutrition profile. Pregnancy/lactation-specific targeting, medical diets, allergies and therapeutic restrictions are outside the MVP.

## Desired outcome

For the 30-day period, the system should make it possible to:
- derive each household member's target energy and macro-/micronutrient specifications from personal parameters and active nutrition standards, preserving the source meaning of reference values, ranges and safety limits;
- aggregate compatible individual nutritional demand into a household target for purchase optimization;
- select a nutritionally reasonable and sufficiently varied set of foods;
- map that set to concrete purchasable goods and merchant offers;
- calculate package quantities, stores, prices, delivery-related costs and the total required budget;
- compare trade-offs between nutritional coverage, variety, total cost and procurement convenience;
- identify nutrient gaps that cannot be reasonably closed with the currently available purchasable catalog and suggest theoretical foods that could close them.

## MVP simplifications

- optimization uses the aggregated household nutritional target; it does not prove that the purchased food can be allocated among members so that every member individually satisfies all of their target and safety conditions;
- actual consumption is not tracked;
- existing household inventory and carry-over leftovers are not considered;
- meals, recipes, cooking, portioning and nutrient changes caused by preparation are not modeled;
- product, nutrition and price data may be entered manually or imported; automatic external data acquisition is not required;
- transport/travel cost between stores is not calculated.
