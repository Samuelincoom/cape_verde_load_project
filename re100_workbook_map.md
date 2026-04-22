## RE100 Workbook Map

Source workbook inspected: `Model RE100 and handbook/RE100 Model Version 1.0 2026.xlsx`

### Workbook structure

Relevant sheets found:

- `Input & Output`
- `Wind and Solar Input`
- `Wind and Solar Output`
- `Hourly Load`
- `Residual load and storage`
- `Solid Biomass`
- `Geothermal Power`
- `Waste to Energy`
- supporting chart/data sheets: `Diagramms year`, `Diagramms April`, `Diagramms Day in April`, `Load profiles`, `Daten (Wulf)`, `Daten Solar (Wulf)`, `Power Curve Wind`

Expected course files that were **not** found locally in this project:

- `Building your own model.pptx`
- `Building your own model.key`
- `100% RE Barbados.ppt`

### Exact input locations used by the model

#### 1. Hourly load input

Main operative load range used by the model:

- `Hourly Load!G7:G8766`

Key related cells:

- `Hourly Load!F7:F8766`: base hourly load curve
- `Hourly Load!H7:H8766`: e-car charging increment
- `Input & Output!K6`: total annual load, formula `=SUM('Hourly Load'!G7:G8766)`
- `Input & Output!C25`: base-year electricity demand from `Hourly Load!F3`
- `Input & Output!C27`: resulting annual demand including cars from `Hourly Load!G3`

Conclusion: for the Santiago case, the cleanest direct load insertion point is `Hourly Load!G7:G8766`.

#### 2. Hourly wind input

Primary weather-input sheet:

- `Wind and Solar Input!D5:D8764`: measured wind speeds at measuring height
- `Wind and Solar Input!D3`: average of the D-column wind speeds

However, the current Barbados template does **not** use column D for active wind generation formulas. The active wind-generation chain is:

- `Wind and Solar Output!B5:B8764` = hub-height wind speed
- current formula pattern: `='Wind and Solar Input'!U5*(C65/C66)^C67`

This means the workbook currently uses:

- `Wind and Solar Input!U5:U8764` as the operative hourly wind series
- `Wind and Solar Input!U1:U3` as related metadata/summary cells

Supporting technical cells:

- `Input & Output!C65`: hub height of wind turbines
- `Input & Output!C66`: measuring height of wind speeds
- `Input & Output!C67`: roughness coefficient
- `Input & Output!C69`: average wind speed at hub height, currently linked to `Wind and Solar Input!D3`

Conclusion: to avoid mixed Barbados/Santiago inputs, the Santiago workflow should either:

1. overwrite the operative wind source cells in column `U`, or
2. relink `Wind and Solar Output!B5:B8764` from column `U` to the Santiago input column intentionally.

#### 3. Hourly solar input

Primary solar input range:

- `Wind and Solar Input!E5:E8764`: total solar radiation

Derived PV production range:

- `Wind and Solar Input!F5:F8764`

Key linked cells:

- `Input & Output!C71`: annual irradiation from `Wind and Solar Input!E3`
- `Input & Output!C72:C75`: PV technical assumptions
- `Wind and Solar Output!D5:D8764`: PV generation, formula pattern `='Wind and Solar Input'!F5*'Input & Output'!C6`

Conclusion: solar radiation should be inserted in `E5:E8764`, then the workbook formulas can continue to derive PV production in column `F`.

#### 4. Scenario capacities and operating constraints

Main scenario input cells on `Input & Output`:

- `C5`: wind power capacity installed (MW)
- `C6`: PV capacity installed (MW)
- `C7`: solid biomass capacity installed (MW)
- `C8`: geothermal capacity installed (MW)
- `C9`: waste-to-energy installed (MW)
- `C10`: start volume storage (MWh)
- `C11`: max storage (MWh)
- `C12`: maximum back-up generation allowed (%)
- `C14`: max pump capacity (MW)
- `C15`: max generator capacity pump storage (MW)

Derived back-up sizing/output cells:

- `C19`: total biodiesel back-up generation (MWh)
- `C20`: total biodiesel demand (t)
- `C23`: necessary biodiesel capacity (MW)

#### 5. Key economic assumptions

Economic input block on `Input & Output`:

- `C36:C42`: technology lifetimes
- `C43:C49`: investment costs
- `C50:C56`: O&M cost assumptions
- `C57:C60`: fuel cost assumptions including biodiesel
- `C61`: interest rate
- `C62:C63`: currency conversion factors

Cost outputs used by the workbook:

- `O82`: `Cost per kWh used` in EUR/kWh
- `P82`: `Cost per kWh used` in local currency / kWh
- `O79`: cost of electricity from biodiesel in EUR/kWh
- `O77`: cost of storage per kWh stored
- `O78`: cost of storage per average kWh used

For scenario comparison, `O82` is the cleanest workbook-native LCOE-like metric.

#### 6. Key technical assumptions

Technical input cells on `Input & Output`:

- `C65`: hub height of wind turbines
- `C66`: measuring height of wind speeds
- `C67`: roughness coefficient
- `C68`: installed wind capacity per km2
- `C69`: average wind speed at hub height
- `C71`: annual irradiation on horizontal surface
- `C72`: module peak capacity
- `C73`: module area required for 1 kWp
- `C74`: area of single module
- `C75`: specific annual PV production
- `C77`: average electrical efficiency for biomass
- `C79`: storage efficiency (one way)
- `C80`: pump storage head

### Main output locations for scenario extraction

Annual electricity balance:

- `Input & Output!K6`: annual load (MWh)
- `Input & Output!K10`: annual wind generation (MWh)
- `Input & Output!K11`: annual PV generation (MWh)
- `Input & Output!K12`: annual renewable generation total before storage/backup grouping
- `Input & Output!K17` or `C19`: biodiesel back-up generation (MWh)
- `Input & Output!C22` or `K19`: total overproduction (MWh)

Storage / backup / residual-load summary:

- `Input & Output!K27`: max storage generation power (from `Residual load and storage!AA2`)
- `Input & Output!L27`: max pump power (from `Residual load and storage!Z2`, sign-adjusted)
- `Input & Output!M27`: storage level in last hour of year
- `Input & Output!N27`: annual energy used for pumping
- `Input & Output!O27`: annual energy generated from storage
- `Input & Output!K13`: residual load 1 not met
- `Input & Output!K16`: residual load 2 not met
- `Input & Output!O82`: cost per kWh used (EUR/kWh)

First-pass Santiago run note:

- In the populated Santiago workbook, `K16` matched `K17` exactly in every tested scenario, so this template behaves as if `K16` is the deficit handed to biodiesel backup rather than final unserved energy.

Hourly storage/backup mechanics live in:

- `Residual load and storage!B7:AB8766` with key columns:
- `B`: hourly load
- `F`: wind generation
- `G`: PV generation
- `H`: hourly biodiesel generation
- `J`: residual load before storage
- `M`: hourly storage activity
- `N`: storage balance
- `O`: storage level
- `P`: excess production
- `Z`: energy used for pumping
- `AA`: energy generated from storage
- `AB`: hourly storage activity summary

### Important workbook risk found during inspection

The workbook contains one inherited external link to an old Barbados workbook:

- `../../../../../../../../../../../Dokumente/!_Ausgelagerte Dateien/!__Word/!_100%_RE/!_100%_RE_Barbados/!_Modellierung/Model 2015/S_B_15_3_sp_15_bio_ex_c.xlsx`

And many formulas in `Residual load and storage` still use `[1]...` external-link style references, especially for:

- `Input & Output`
- `Solid Biomass`
- `Geothermal Power`
- a non-present `Run of River Hydro` sheet name

This means the workbook should be treated as a template that needs careful relinking/recalculation before scenario results are accepted as final.

### Practical implication for the Santiago workflow

To build a first Santiago-ready workbook version, the required minimum actions are:

1. copy the original workbook to a new Santiago workbook
2. insert Santiago hourly load into `Hourly Load!G7:G8766`
3. insert Santiago hourly wind into the workbook’s active wind input path
4. insert Santiago hourly solar radiation into `Wind and Solar Input!E5:E8764`
5. force recalculation in Excel
6. verify that the external-link leftovers are not contaminating scenario outputs
