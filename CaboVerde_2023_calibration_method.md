# Cabo Verde 2023 Calibration Method

- Created: 2026-04-18T17:23:01Z
- Source file used: `CaboVerde_2023_hourly_load_clean.csv`
- Original annual total: 520312.940000 MWh (520.313 GWh)
- Target annual total: 572900.0 MWh (572.9 GWh)
- Calibrated annual total achieved: 572900.000000 MWh (572.900 GWh)
- Scaling factor applied uniformly to every hourly Cabo Verde load value: 1.101068137956
- Residual adjustment on the final hour to hit the exact target total: 0.000000000000 MWh
- Cabo Verde data status: estimated, not reported.
- Santiago data status: proxy, not measured.

## Interpretation

- The calibrated Cabo Verde series preserves the original hourly shape and changes only the scale.
- The regenerated Santiago proxy uses the calibrated national hourly shape as its starting point.
- The Santiago file remains a modeled proxy and should not be treated as measured island demand.
