# Class-Ready Santiago RE100 Summary

## Case definition

- Case: Santiago island first-pass RE100 workbook run.
- Load basis: calibrated Santiago proxy derived from the Cabo Verde national Electricity Maps load shape.
- Weather basis: 2023 NASA POWER hourly weather for a representative point near Praia after Renewables.ninja rejected 2023 requests.
- Workbook basis: `RE100_CapeVerde_Santiago_v1.xlsx`, recalculated twice in Excel before this pack was written.

## Scenario A currently loaded in the workbook

- Wind capacity: `40 MW`
- PV capacity: `100 MW`
- Start storage: `225 MWh`
- Max storage: `450 MWh`
- Backup limit: `5.0%`

## Scenario A headline results

- Annual load served in workbook: `320.824 GWh`
- Annual wind generation: `191.041 GWh`
- Annual PV generation: `204.954 GWh`
- Annual biodiesel backup generation: `15.153 GWh`
- Biodiesel backup share: `4.72%`
- Annual overproduction: `63.759 GWh`
- Workbook cost-per-kWh-used metric (`O82`): `0.0929 EUR/kWh`

## Interpretation

- Scenario A remains the most presentation-ready first-pass option because it stays under the 5% backup limit while keeping the workbook cost lower than the other feasible tested cases.
- Scenario C is still worth discussing as the lower-backup alternative because its backup share is smaller, but it comes with a slightly higher workbook cost metric.
- The workbook's `K16` cell mirrors biodiesel generation in this template, so it is treated here as the energy handed to backup rather than final unserved load.

## Recalculation check

- Workbook recalculation consistency: `passed`.
- Check method: force full Excel recalculation twice and compare the key Scenario A output cells.

## Figure pack

- `scenario_A_figures/01_weekly_load_generation.svg`
- `scenario_A_figures/02_monthly_energy_balance.svg`
- `scenario_A_figures/03_weekly_storage_level.svg`
- `scenario_A_figures/04_peak_backup_week.svg`
- `scenario_A_figures/05_residual_load_duration_curve.svg`

## Main cautions for class presentation

- Santiago load is proxy-based, not metered.
- Santiago wind and solar are representative-point weather inputs, not measured plant output.
- Technology cost inputs still come from the course workbook template and should later be localized.
