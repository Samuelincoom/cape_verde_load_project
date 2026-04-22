# Weather Source Note

- Target case: Santiago island, represented by a point near Praia at `14.92, -23.51`.
- Reason for point choice: Praia is the island's main demand center and provides a transparent, reproducible representative point for a first workbook run.
- Renewables.ninja attempted first: `HTTP 400`.
- Renewables.ninja message: `Error: 
date_to must be 2019-12-31 or earlier`.
- Renewables.ninja could not provide 2023 hourly data for this run, so it was used only as the first-choice check, not as the final weather source.
- Final weather source used: `NASA POWER Hourly API`.
- Wind series used: `WS10M` from NASA POWER in m/s at 10 m height, aligned to UTC.
- Solar series used: `ALLSKY_SFC_SW_DWN` from NASA POWER in Wh/m^2 per hour, converted to `kW/m^2` by dividing by 1000 for workbook compatibility.
- Load timestamps already in this project are UTC (`...Z`), so the weather series were also kept in UTC for direct hourly alignment.
- Wind and solar are weather-based proxy inputs for Santiago, not on-island measured plant output data.

## NASA POWER metadata

- Header title: `NASA/POWER Source Native Resolution Hourly Data`.
- API version: `v2.8.9`.
- Source stack: `SYN1DEG, MERRA2, POWER`.
- Wind units: `m/s`.
- Solar units before conversion: `Wh/m^2`.
