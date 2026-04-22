# Input Replacement Log

## Workbook target

- Target workbook copy: `RE100_CapeVerde_Santiago_v1.xlsx`
- Original workbook left unchanged: `Model RE100 and handbook/RE100 Model Version 1.0 2026.xlsx`

## Load replacement

- Source file used: `Santiago_2023_proxy_hourly_load_calibrated.csv`
- Status: Santiago load remains proxy-based, not measured.
- Workbook path affected:
- `Hourly Load!F7:F8766` written with the Santiago hourly proxy values
- `Hourly Load!H7:H8766` written as zero additional car-charging load
- `Hourly Load!G7:G8766` then continues as the workbook's operative load path through the existing formula chain

## Wind replacement

- Preferred source checked first: `Renewables.ninja`
- 2023 result: rejected by the live service because `date_to must be 2019-12-31 or earlier`
- Final source used: `Santiago_2023_hourly_wind.csv`
- Weather basis: NASA POWER hourly `WS10M` at a representative Santiago/Praia point
- Workbook paths affected:
- `Wind and Solar Input!D5:D8764` written with Santiago hourly 10 m wind speeds
- `Wind and Solar Input!U5:U8764` also written with the same Santiago hourly wind speeds because the active Barbados template formulas still pull wind from column `U`

## Solar replacement

- Final source used: `Santiago_2023_hourly_solar.csv`
- Weather basis: NASA POWER hourly `ALLSKY_SFC_SW_DWN`
- Conversion used before workbook insertion: `Wh/m²` to `kW/m²` by dividing by `1000`
- Workbook path affected:
- `Wind and Solar Input!E5:E8764` written with Santiago hourly solar radiation values

## Workbook hygiene adjustments

- Cleared inherited external-link helper formulas in `Residual load and storage!V:Y` to avoid stale Barbados references.
- Replaced selected external-style references in `Residual load and storage` with local-sheet references where possible.
- Forced full Excel recalculation after input replacement and before exporting results.

## Scenario state saved in the workbook

- Current saved scenario: Scenario A
- Scenario A settings:
- `40 MW` wind
- `100 MW` PV
- `225 MWh` start storage
- `450 MWh` max storage
- `5%` biodiesel backup limit
