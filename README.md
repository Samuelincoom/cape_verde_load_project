# Cabo Verde Load Proejct

ok guys, this repo is our shared workspae for the Cabo Verde 2023 hourly load datset and the Santiago proxy exercise.

## What this repo does

the main goal here is to keep the anlysis easy to follow for the group:

- pull the Cabo Verde load series from Electricity Maps
- save the raw API responses and validation notes
- build a calibirated national series that hits 572.9 GWh exactly
- regenrate the Santiago proxy from the calibrated national shape
- keep the whole thing re-useable for future coursework

## Important caveats

pleease keep these points in mind when we talk about the results:

- the raw version of Cabo Verde series in this repo is estimated to 90% accuracy and 80% accurate, not reported. like i said, we wait to see if the governemnt will respond to our email
- again, also the Santiago file is proxy, not measured
- this is fine for academic coursework and class discusion. the 80% is more than fine
- so this is not an officail utility planning dataset

## Main files

- `fetch_cape_verde_load.py`: gets the zone info, hourly series, validation, and exports
- `calibrate_cape_verde_load.py`: scales the national series to the benchmark total
- `CaboVerde_2023_hourly_load_clean.csv`: the clean natonal hourly dataset
- `CaboVerde_2023_hourly_load_calibrated.csv`: the benchmark-matched national dataset
- `Santiago_2023_proxy_hourly_load_calibrated.csv`: the calibrated Santiago proxy
- `CaboVerde_2023_validation.md`: summary of what endpoint worked and what the data meens
- `CaboVerde_2023_calibration_method.md`: short method note for the calibrated version

## How to use it

if we need to rerun everthing later, the rough flow is:

1. run `fetch_cape_verde_load.py`
2. inspect the validation and zone notes
3. run `calibrate_cape_verde_load.py`
4. use the CSV or XLSX outputs for tables, charts, and writeups

## Group note

ok guys, if something looks a bit wierd in the files, check the method notes first becuase they explain what is real, what is scaled, and what is modeled. just like what i explained in the whatsapp messages i texted
