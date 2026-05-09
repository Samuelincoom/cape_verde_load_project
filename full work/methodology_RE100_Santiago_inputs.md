# Santiago RE100 input pack for Prof. Hohmeyer's model

This pack does not create a new energy model. It fills Prof. Hohmeyer's existing `RE100 Model Version 1.0 2026.xlsx` with sourced Santiago, Cabo Verde input vectors and documented scenario assumptions.

## Base year
The base year is 2023. It has exactly 8760 hours and matches the workbook structure. 2024 was not used because it is a leap year with 8784 hours.

## Load input
- Target range: `Hourly Load!F7:F8766`
- Unit: MWh/h, equivalent to MW for a one-hour timestep
- Annual anchor: 263,839.489 MWh from Electra 2023 Santiago production
- Peak anchor: 41.833 MW on 2023-08-28 15:00
- Filled annual total: 263,839.489 MWh
- Filled peak: 42.040 MW

Official annual energy accuracy is 100% against Electra 2023 Santiago total. Peak check is approximately 99.5%. Hour-by-hour measured accuracy cannot be certified without the operator's real 8760-hour meter record.

## Wind input
- Target range: `Wind and Solar Input!D5:D8764`
- Source: Open-Meteo Historical API hourly wind_speed_10m
- Site: Santiago wind farm / Monte de Sao Filipe representative point
- Coordinates: 15.0855, -23.6245
- Unit: m/s
- Measurement height: 10 m, so `Input & Output!C66 = 10`

## Solar input
- Target range: `Wind and Solar Input!E5:E8764`
- Source: Open-Meteo Historical API hourly shortwave_radiation
- Site: Santiago/Palmarejo PV representative point
- Coordinates: 14.9103, -23.5437
- Conversion: kW/m2 = W/m2 / 1000
- NASA POWER cross-check: {'status': 'available', 'api_url': 'https://power.larc.nasa.gov/api/temporal/hourly/point?parameters=ALLSKY_SFC_SW_DWN&community=RE&longitude=-23.5437&latitude=14.9103&start=20230101&end=20231231&format=JSON&time-standard=LST', 'annual_kwh_m2': 2172.51061, 'points': 8760}

## Scenario and default assumptions
The model workbook is filled with the `Conservative start` scenario in `Input & Output!C5:C12`. Additional `Wind-heavy` and `PV-heavy` assumptions are included in the `Santiago_Scenarios` sheet. Values marked D are scenario assumptions or model defaults, not verified Santiago measurements.

## Electricity Maps
Electricity Maps is used only if a local CSV exists. It is not official Santiago hourly meter data. It is a Cabo Verde national shape benchmark. Current status: {'metric': 'status', 'value': 'Skipped: no Electricity Maps CSV and no ELECTRICITYMAPS_TOKEN environment variable.', 'notes': 'Electricity Maps would only be a Cabo Verde national shape benchmark, not Santiago hourly truth.'}.

## Confidence classes
A = official measured or official annual data. B = official report value transformed by clear calculation. C = scientific dataset or reanalysis weather source. D = model default or scenario assumption. E = missing, not used.

Confidence counts: {'D': 43, 'B': 4, 'C': 3, 'A/B/C': 1}

## Output files
- `RE100_Model_Santiago_2023_filled.xlsx`
- `Santiago_RE100_Input_Audit.xlsx`
- `Santiago_RE100_Input_Audit.csv`
- `santiago_re100_required_inputs.csv`
- `methodology_RE100_Santiago_inputs.md`
