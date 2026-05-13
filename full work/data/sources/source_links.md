# Source Links

## 1. DTU Cape Verde Reference System

Use: Santiago load profile.

File: `SantiagoData_v4.xlsx`.

Sheet: `Equivalent Week Profile Load`.

Link: https://data.dtu.dk/articles/dataset/Cape_Verde_Reference_System_v2_0/17430413

## 2. Electra 2023 Annual Report

Use: Santiago 2023 annual production and peak validation.

Page: page 25 for annual Santiago production.

Page: page 26 for Santiago peak.

Link: https://www.mf.gov.cv/documents/20126/4493539/RContas_Electra%2BSA%2B2023.pdf/49cabfe7-ec19-fa6f-dcea-7115b5dade7f?download=true&t=1716468826573&version=1.0

## 3. Prof. Hohmeyer RE100 Handbook

Use: tells us where model inputs go.

Pages: page 15 and page 16 for hourly load, wind speed, and solar radiation inputs.

Pages: page 19 to page 22 for economic and technical input cells.

Sharing note: the handbook is not uploaded here because permission to redistribute it was not confirmed.

## 4. Open-Meteo Historical Weather API

Use: hourly wind speed and solar radiation for Santiago 2023.

Documentation: https://open-meteo.com/en/docs/historical-weather-api

Exact request URL used:

https://archive-api.open-meteo.com/v1/archive?latitude=14.9167&longitude=-23.5167&start_date=2023-01-01&end_date=2023-12-31&hourly=wind_speed_100m,shortwave_radiation&wind_speed_unit=ms&timezone=Atlantic%2FCape_Verde

## 5. NASA POWER Hourly API

Use: independent weather cross-check if downloaded.

Documentation: https://power.larc.nasa.gov/docs/services/api/temporal/hourly/

Exact request URL attempted:

https://power.larc.nasa.gov/api/temporal/hourly/point?parameters=WS10M,ALLSKY_SFC_SW_DWN&community=RE&longitude=-23.5167&latitude=14.9167&start=20230101&end=20231231&format=JSON&time-standard=LST

## 6. Electricity Maps Cabo Verde

Use: benchmark only, not final Santiago load source.

Important note: Electricity Maps Cabo Verde represents the national Cabo Verde zone, not Santiago-only operator data. It is not used as final Santiago load input.

Documentation: https://portal.electricitymaps.com/docs/api

Methodology: https://www.electricitymaps.com/research
