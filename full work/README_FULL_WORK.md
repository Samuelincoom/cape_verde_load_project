# Full Santiago RE100 Work Package

Open first: `Santiago_RE100_Input_Audit.xlsx`.

This folder is the GitHub evidence package for the Santiago Island, Cabo Verde, 2023 input pack prepared for Prof. Hohmeyer's RE100 Excel model. It is not a new energy model. It documents and packages the Santiago-specific inputs, source trail, validation checks, and generated load-curve evidence used to run the existing RE100 workbook locally.

## Files

- `Santiago_RE100_Input_Audit.xlsx`: Main audit workbook. It lists the required RE100 input cells/ranges, values, units, sources, confidence classes, validation checks, and source notes.
- `Santiago_RE100_Input_Audit.csv`: CSV export of the required-input audit table for version control and quick review.
- `methodology_RE100_Santiago_inputs.md`: Methodology note explaining load, wind, solar, scenario, economic, and technical assumptions.
- `santiago_hourly_load_2023_reconstructed.csv`: 8760-hour Santiago reconstructed load input for 2023.
- `santiago_hourly_load_2023_reconstructed.xlsx`: Excel version of the reconstructed hourly load curve with validation and charts.
- `sources/source_links.md`: Public source links and local-source notes.
- `prompts/codex_prompt_RE100_Santiago.txt`: Reproducibility prompt used to generate the Santiago RE100 input pack.
- `presentation/Santiago_Load_Curve_Method_Presentation_ElectricityMaps_Update.pptx`: Short presentation summarizing the load method, Electricity Maps caveat, and RE100 input-pack connection.

## Copyright-Sensitive Model File

`RE100_Model_Santiago_2023_filled.xlsx` was generated locally from Prof. Hohmeyer's original workbook, but it is not redistributed in this GitHub package unless the user confirms permission to share derivative copies of the professor's workbook. The local generated file remains at:

`C:\Users\Fiifi\Downloads\CapeVerdeReferenceSystemData_v002\Santiago_RE100_Input_Pack\RE100_Model_Santiago_2023_filled.xlsx`

The original professor workbook and handbook were used locally only and are not included here.

## Load Method

The Santiago hourly load curve was reconstructed from `SantiagoData_v4.xlsx` in the DTU Cape Verde Reference System, using the `Equivalent Week Profile Load` sheet. For each 2023 timestamp, the method maps the month and weekday to the DTU representative equivalent day:

`equivalent_day = (month - 1) * 7 + weekday_number`

where Monday is 1 and Sunday is 7. The DTU profile values are treated as a relative load-shape index and scaled so the annual total equals Electra's official Santiago 2023 annual production:

`263,839,489 kWh = 263,839.489 MWh = 263.839489 GWh`

Official annual energy accuracy is therefore 100% against the Electra 2023 Santiago total by scaling. The hourly values remain reconstructed estimates, not certified SCADA measurements.

## RE100 Model Connection

The prepared inputs target the professor's existing workbook ranges:

- Hourly load: `Hourly Load!F7:F8766`
- Hourly wind speed: `Wind and Solar Input!D5:D8764`
- Hourly solar radiation: `Wind and Solar Input!E5:E8764`
- Scenario and technology assumptions: `Input & Output` yellow/user-editable cells documented in the audit workbook

The audit workbook marks each value with a confidence class:

- A: official measured or official annual data
- B: official report value transformed by clear calculation
- C: scientific dataset or reanalysis weather source
- D: model default or scenario assumption
- E: missing or not used

## Official vs Reconstructed

Official data used:

- Santiago 2023 annual production from Electra 2023 report
- Santiago 2023 reported peak from Electra 2023 report

Reconstructed or modeled data:

- Hourly Santiago load shape from DTU Santiago-specific reference-system profiles
- Hourly wind and solar weather vectors from public reanalysis/API sources
- Scenario capacities and storage values marked as scenario assumptions, not verified existing Santiago assets

Electricity Maps Cabo Verde data, when available, is used only as a national zone shape benchmark. It is not official Santiago hourly meter data and must not be treated as Santiago SCADA truth.
