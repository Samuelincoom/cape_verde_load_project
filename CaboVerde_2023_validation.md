# Cabo Verde 2023 Validation Note

- Generated: 2026-04-18T16:36:35Z
- Santiago exists as a separate zone: No
- Chosen zone: `CV`
- Endpoint used: `/total-load/past-range`
- Data source classification: real Electricity Maps processed total-load endpoint, but all hours are estimated rather than directly reported
- Estimated hours: 8760
- Estimated share: 100.00%
- Annual total: 520312.940 MWh (520.313 GWh)
- Missing hours after cleaning: 0
- Duplicate timestamps before cleaning: 0
- Null load values after cleaning: 0
- Timezone consistency: Consistent UTC-style timestamps (Z)
- 8760-row result achieved: Yes
- External benchmark used: 572.9 GWh
- Benchmark delta: -52.587 GWh (-9.18%)
- Benchmark interpretation: The 572.9 GWh benchmark is directly comparable because the chosen zone is country-level Cabo Verde.
- Academic suitability: Suitable for academic coursework only with explicit caveats: it is a real Electricity Maps API series, but for Cabo Verde in 2023 it comes from the processed total-load endpoint and every hour is estimated rather than directly reported.

## Cleaning Steps

- Parsed API timestamps to timezone-aware UTC datetimes.
- Sorted rows by timestamp, preferring non-null and non-estimated values when duplicate timestamps existed.
- Dropped duplicate timestamps after sorting.
- Reindexed to the full 2023 hourly scaffold (8760 hours) and left missing load values blank instead of inventing replacements.
- Did not smooth, interpolate, or otherwise alter real API load values.
