# RE100 Input Mapping for Santiago 2023

## Load

Goes into: `Hourly Load!F7:F8766`

Unit: MWh/h, same as MW for one hour.

Source: reconstructed Santiago 2023 hourly load curve from DTU Santiago profile scaled to Electra's official Santiago annual production.

## Wind

Goes into: `Wind and Solar Input!D5:D8764`

Unit: m/s.

Source variable: Open-Meteo `wind_speed_100m`.

Important: set the measurement height in Prof. Hohmeyer's model to 100 m if using `wind_speed_100m`. The matching input cell is `Input & Output!C66 = 100`.

## Solar

Goes into: `Wind and Solar Input!E5:E8764`

Unit: kW/m2.

Source variable: Open-Meteo `shortwave_radiation`.

Conversion: Open-Meteo gives W/m2, so the model input is W/m2 divided by 1000.

## Caution

These weather data are Open-Meteo reanalysis/modelled historical weather data, not measured wind mast or on-site pyranometer observations. They are usable public hourly inputs, but they are not verified site measurements.
