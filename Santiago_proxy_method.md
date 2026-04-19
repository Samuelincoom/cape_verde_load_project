# Santiago Proxy Method

This file describes a modeled Santiago hourly load proxy. It is not measured Santiago data.

- Generated: 2026-04-18T16:36:36Z
- Source shape zone: `CV`
- Population share assumption: 56.00%
- Base-load adjustment: 5.00%
- Seasonality strength: 10.00%
- Proxy annual total: 291375.246 MWh (291.375 GWh)

## Method

- Step 1: start from the real Cabo Verde hourly shape returned by Electricity Maps.
- Step 2: scale each hour by a transparent Santiago population-share assumption.
- Step 3: apply a simple base-load adjustment by pulling each hourly value 5% toward a flat annual mean component.
- Step 4: apply a transparent seasonality adjustment derived from the real Cabo Verde monthly pattern, with only a modest 10% amplification of monthly deviations from the annual mean.
- Step 5: renormalize the modeled series so its annual total still matches the population-share-scaled Cabo Verde annual total.

## Interpretation

- This proxy is modeled, not measured.
- It should be treated as a sensitivity or coursework approximation for Santiago when no separate Santiago/Praia Electricity Maps zone is available.
- It is suitable for transparent exploratory academic use, but not as a substitute for a metered Santiago system-load time series.
