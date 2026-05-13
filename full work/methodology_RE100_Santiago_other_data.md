# Methodology for Santiago Wind and Solar RE100 Inputs

## 1. What we needed

We needed the other hourly data that Prof. Hohmeyer's RE100 model needs for Santiago. Thiss means hourly wind speed and hourly solar radiation for the same 8760-hour year as the load curve.

## 2. How we got load

We did not rebuild the load curve. We used the existing Santiago reconstructed 2023 load file already in the project. It has 8760 rows and an annual total close to 263.839 GWh.

## 3. How we got wind

We used the Open-Meteo Historical Weather API for Santiago/Praia coordinates. The wind variable is `wind_speed_100m`, which means wind speed 100 m above ground. This is modelled or reanalysis weather data, not a measured wind mast file.

## 4. How we got solar

We used Open-Meteo `shortwave_radiation`. Solar radiation means sunlight energy reaching the ground. This is also modelled or reanalysis weather data, not a verified solar station measurement.

## 5. How we converted the units

Open-Meteo gave solar radiation in W/m2. Prof. Hohmeyer's model needs kW/m2, so we divided by 1000. The wind wass requested directly in m/s, so no speed conversion was needed.

## 6. Where the values go in Prof. Hohmeyer's model

Load goes into `Hourly Load!F7:F8766`.

Wind goes into `Wind and Solar Input!D5:D8764`.

Solar goes into `Wind and Solar Input!E5:E8764`.

Because the wind source is 100 m wind speed, the model measurement height should be set to 100 m in `Input & Output!C66`.

## 7. What is official

The official load anchors are Electra's Santiago 2023 annual production and peak values. Those come from the Electra 2023 annual report.

## 8. What is reconstructed

The hourly load shape is reconstructed from DTU Santiago-specific load-profile data. The wind and solar are public hourly weather model or reanalysis data from Open-Meteo. They are not official measured Santiago wind and solar station data.

## 9. What still needs care

We should not call this exact measured 8760-hour Santiago energy-system data. It is a strong public input pack for running the professor's model, but official operator SCADA and measured site weather data would be better if they become available. A small NASA POWER cross-check was also attempted so the weather input is not just accepted without any outside comparison.
