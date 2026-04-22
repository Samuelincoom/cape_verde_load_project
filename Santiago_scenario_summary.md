# Santiago Scenario Summary

- Most promising first-pass scenario: `A`.
- Best scenario among A-C before storage sensitivity: `A`.
- Interpretation rule used: prioritize scenarios that respect the stated backup limit and then minimize workbook cost per kWh used; in this template `K16` is interpreted as the deficit passed to backup rather than final unserved load.

## Scenario results

### Scenario A

- Wind: `40 MW`
- PV: `100 MW`
- Storage: `450 MWh`
- Backup limit: `5.0%`
- Biodiesel backup generation: `15.153 GWh`
- Backup share: `4.72%`
- Overproduction: `63.759 GWh`
- LCOE-like workbook metric (`O82`): `0.0929 EUR/kWh`
- Remaining deficit handed to backup in workbook cell `K16`: `15153.462 MWh`
- First-pass assessment: `No obvious first-pass failure`

### Scenario B

- Wind: `55 MW`
- PV: `70 MW`
- Storage: `450 MWh`
- Backup limit: `5.0%`
- Biodiesel backup generation: `22.016 GWh`
- Backup share: `6.86%`
- Overproduction: `84.749 GWh`
- LCOE-like workbook metric (`O82`): `0.0925 EUR/kWh`
- Remaining deficit handed to backup in workbook cell `K16`: `22016.380 MWh`
- First-pass assessment: `Biodiesel share exceeds scenario backup limit`

### Scenario C

- Wind: `30 MW`
- PV: `125 MW`
- Storage: `450 MWh`
- Backup limit: `5.0%`
- Biodiesel backup generation: `9.316 GWh`
- Backup share: `2.90%`
- Overproduction: `54.154 GWh`
- LCOE-like workbook metric (`O82`): `0.0946 EUR/kWh`
- Remaining deficit handed to backup in workbook cell `K16`: `9316.268 MWh`
- First-pass assessment: `No obvious first-pass failure`

### Scenario D

- Wind: `40 MW`
- PV: `100 MW`
- Storage: `700 MWh`
- Backup limit: `2.5%`
- Biodiesel backup generation: `11.378 GWh`
- Backup share: `3.55%`
- Overproduction: `59.321 GWh`
- LCOE-like workbook metric (`O82`): `0.0960 EUR/kWh`
- Remaining deficit handed to backup in workbook cell `K16`: `11377.851 MWh`
- First-pass assessment: `Biodiesel share exceeds scenario backup limit`

### Scenario E

- Wind: `40 MW`
- PV: `100 MW`
- Storage: `250 MWh`
- Backup limit: `5.0%`
- Biodiesel backup generation: `21.417 GWh`
- Backup share: `6.68%`
- Overproduction: `71.002 GWh`
- LCOE-like workbook metric (`O82`): `0.0930 EUR/kWh`
- Remaining deficit handed to backup in workbook cell `K16`: `21416.683 MWh`
- First-pass assessment: `Biodiesel share exceeds scenario backup limit`
