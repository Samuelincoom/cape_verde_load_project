# Current Data Inventory

## Existing load and proxy files

- `CaboVerde_2023_hourly_load_clean.csv`
  - 8760 hourly rows for 2023.
  - Columns: `timestamp`, `zone`, `load_value`, `unit`, `isEstimated`, `source_endpoint`.
  - Annual total: 520.313 GWh.
  - Based on Electricity Maps `CV` country-level data because no separate Santiago/Praia zone was available.

- `CaboVerde_2023_hourly_load.xlsx`
  - Workbook export of the same clean national hourly series.

- `CaboVerde_2023_validation.md`
  - Records that Santiago did not exist as a separate Electricity Maps zone.
  - Records that `/total-load/past-range` was used after `/total-reported-load/past-range` returned no usable data.
  - Notes that the Cabo Verde series is estimated, not reported, for all 8760 hours.

- `CaboVerde_2023_hourly_load_calibrated.csv`
  - 8760 hourly rows.
  - Uniformly scaled version of the Cabo Verde hourly series.
  - Annual total calibrated to 572.900 GWh exactly.

- `CaboVerde_2023_hourly_load_calibrated.xlsx`
  - Workbook export of the calibrated national series.

- `CaboVerde_2023_calibration_method.md`
  - Records the original total, target total, and uniform scaling factor.
  - Notes that Cabo Verde remains estimated, not reported.

- `Santiago_2023_proxy_hourly_load.csv`
  - 8760 hourly rows.
  - Santiago hourly load proxy built from the original Cabo Verde hourly shape.
  - Annual total: 291.375 GWh.
  - Clearly proxy-based, not measured.

- `Santiago_2023_proxy_hourly_load_calibrated.csv`
  - 8760 hourly rows.
  - Santiago hourly load proxy regenerated from the calibrated Cabo Verde hourly shape.
  - Annual total: 320.824 GWh.
  - This is the strongest Santiago load starting point currently available in the repo.

- `Santiago_2023_proxy_hourly_load_calibrated.xlsx`
  - Workbook export of the calibrated Santiago proxy series.

- `Santiago_proxy_method.md`
  - Describes the Santiago proxy method.
  - Notes the population-share assumption, base-load adjustment, and seasonality adjustment.

## Existing supporting provenance

- `raw_api_responses/`
  - Preserved Electricity Maps raw responses for zone checks and hourly chunk pulls.

- `zones_raw.json`
  - Raw zone-check payloads.

- `zones_summary.md`
  - Human-readable zone selection summary for Cabo Verde / Santiago.

- `fetch_attempt_log.json`
  - Records endpoint fallback behavior for the Electricity Maps fetch workflow.

## Existing helper scripts

- `fetch_cape_verde_load.py`
  - Builds the Cabo Verde hourly load dataset, validation note, and Santiago proxy when needed.

- `calibrate_cape_verde_load.py`
  - Calibrates the national Cabo Verde hourly series to the benchmark annual total and regenerates the Santiago calibrated proxy.

## Course-model source files currently found locally

- `Model RE100 and handbook/RE100 Model Version 1.0 2026.xlsx`
- `Model RE100 and handbook/Handbook 100% RE.pdf`

## Course files referenced in the request but not currently found in the local folder

- `Building your own model.pptx / .key`
- `100% RE Barbados.ppt`

## RE100 stage outputs now present

- `re100_workbook_map.md`
  - Maps the workbook sheets, operative hourly input ranges, scenario cells, and output cells.
  - Flags the inherited Barbados external-link issue and the workbook-behavior note for `K16`/`K17`.

- `Santiago_2023_hourly_wind.csv`
  - 8760 hourly Santiago/Praia representative-point wind rows for 2023 in UTC.
  - Final source used: NASA POWER fallback after Renewables.ninja rejected 2023.

- `Santiago_2023_hourly_solar.csv`
  - 8760 hourly Santiago/Praia representative-point solar rows for 2023 in UTC.
  - Solar radiation converted into workbook-compatible `kW/m²`.

- `weather_source_note.md`
  - Documents that Renewables.ninja was tried first.
  - Records the 2023 rejection and the NASA POWER fallback.

- `RE100_CapeVerde_Santiago_v1.xlsx`
  - Working Santiago workbook copy with Santiago inputs inserted.
  - Currently saved with the most promising first-pass scenario loaded.

- `Santiago_case_method_note.md`
  - Documents the Santiago load proxy, weather source choice, and workbook-interpretation assumptions.

- `Santiago_scenario_comparison.csv`
- `Santiago_scenario_comparison.xlsx`
  - First scenario batch comparison outputs for scenarios A-E.

- `Santiago_scenario_summary.md`
  - Short narrative summary of the scenario batch and first-pass interpretation.

- `explain_like_im_a_student.md`
  - Plain-English explanation of what was real, what was proxy, and what the first scenario results mean.

## Remaining weak spots

- Santiago load is still proxy-based rather than operator-measured.
- Santiago weather still uses one representative point near Praia rather than island-wide measured data.
- Workbook costs and technical assumptions still come from the course template and should be localized later if better Santiago/Cabo Verde assumptions become available.
