# Explain Like I'm A Student

This workbook run uses three kinds of inputs.

- The load curve is based on a real Cabo Verde hourly series from Electricity Maps, but Santiago itself did not exist as a separate zone, so the Santiago load is a modeled proxy based on the calibrated national shape.
- The wind and solar inputs are not plant meter data from Santiago. Renewables.ninja was tested first, but it would not supply 2023 hourly data. So the weather inputs came from NASA POWER for a representative point near Praia on Santiago.
- The scenario results themselves come from the RE100 workbook logic after the Santiago inputs were inserted and the workbook was recalculated in Excel.

What was real:

- The underlying Cabo Verde national hourly load shape.
- The calibrated national annual electricity scale.
- The 2023 NASA POWER hourly weather record used for the Santiago representative point.

What was proxy or modeled:

- Santiago hourly electricity load.
- Santiago weather representativeness, because one point near Praia stands in for the whole island.
- The scenario capacities themselves, which are planning assumptions rather than historical facts.

What the first scenario results mean:

- Each scenario tests a different mix of wind, PV, and storage for meeting the Santiago proxy load.
- Biodiesel is treated as backup and its share is compared against the scenario limit.
- Storage helps shift excess wind/PV energy into later hours, so the key trade-off is between backup share, overproduction, and cost.
- The workbook's cost result is the `Cost per kWh used` metric from cell `O82`, which works like a workbook-native LCOE-style indicator.

What still needs improvement later:

- Real operator load data for Santiago instead of a population-based proxy.
- Real island weather or plant production data instead of a single representative reanalysis point.
- Local Santiago technology-cost assumptions instead of the template defaults inherited from the course workbook.
- A broader scenario search after the first-pass batch to check whether the current "best" case remains best under more combinations.

At this stage, scenario `A` looks most promising in the first pass because it gives the best balance of backup compliance, residual-load coverage, and workbook cost among the tested cases.
