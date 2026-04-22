# Santiago Case Method Note

- Workbook used: `RE100 Model Version 1.0 2026.xlsx`, copied to `RE100_CapeVerde_Santiago_v1.xlsx`.
- Target case: Santiago island.
- Santiago load input: `Santiago calibrated proxy load from Cabo Verde calibrated national shape`.
- Santiago load status: proxy, not measured.
- Santiago calibrated annual load used in workbook: `320.824 GWh`.
- Weather source requested first: `Renewables.ninja`.
- Renewables.ninja outcome: rejected 2023 hourly request because the live API only allowed dates through `2019-12-31`.
- Weather source actually used: `NASA POWER Hourly API fallback after Renewables.ninja 2023 rejection`.
- Wind series inserted: hourly `WS10M` at 10 m in UTC.
- Solar series inserted: hourly `ALLSKY_SFC_SW_DWN`, converted from Wh/m^2 to kW/m^2 for workbook compatibility.
- Representative location used for Santiago weather: `Praia, Santiago Island, Cabo Verde (14.92, -23.51)`.
- Storage start-volume assumption for every scenario: `50%` of maximum storage volume.
- Biomass, geothermal, and waste-to-energy capacities were kept effectively at zero for this first-pass scenario batch.
- Workbook hygiene step: stale Barbados external-link artifacts were cleared or replaced before recalculation.
- Workbook interpretation note: in this template, `Residual Load 2 not met` (`K16`) numerically matches biodiesel generation (`K17`), so it is treated here as the amount handed off to backup rather than final unserved energy.
- Workbook result currently loaded in `RE100_CapeVerde_Santiago_v1.xlsx`: scenario `A` with wind `40 MW`, PV `100 MW`, storage `450 MWh`, backup limit `5.0%`.
