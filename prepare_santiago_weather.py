from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd
import requests


PROJECT_DIR = Path(__file__).resolve().parent
RAW_DIR = PROJECT_DIR / "weather_raw"

RENEWABLES_NINJA_MODELS_URL = "https://www.renewables.ninja/api/models"
RENEWABLES_NINJA_WIND_URL = "https://www.renewables.ninja/api/data/wind"
NASA_POWER_HOURLY_URL = "https://power.larc.nasa.gov/api/temporal/hourly/point"

REPRESENTATIVE_LOCATION = "Praia, Santiago Island, Cabo Verde"
LATITUDE = 14.92
LONGITUDE = -23.51
YEAR = 2023


@dataclass
class WeatherSourceDecision:
    primary_source: str
    fallback_source: str
    renewables_ninja_status: str
    renewables_ninja_message: str
    latitude: float
    longitude: float


def _session() -> requests.Session:
    session = requests.Session()
    session.trust_env = False
    return session


def _ensure_dirs() -> None:
    RAW_DIR.mkdir(exist_ok=True)


def try_renewables_ninja_2023() -> Tuple[dict, requests.Response]:
    session = _session()
    models_response = session.get(RENEWABLES_NINJA_MODELS_URL, timeout=60)
    models_response.raise_for_status()

    wind_probe_params = {
        "lat": LATITUDE,
        "lon": LONGITUDE,
        "date_from": f"{YEAR}-01-01",
        "date_to": f"{YEAR}-12-31",
        "capacity": 1.0,
        "height": 10,
        "turbine": "Vestas V80 2000",
        "format": "json",
        "raw": "true",
    }
    wind_probe_response = session.get(
        RENEWABLES_NINJA_WIND_URL,
        params=wind_probe_params,
        timeout=120,
    )
    return models_response.json(), wind_probe_response


def fetch_nasa_power_hourly_2023() -> dict:
    session = _session()
    params = {
        "parameters": "WS10M,ALLSKY_SFC_SW_DWN",
        "community": "RE",
        "longitude": LONGITUDE,
        "latitude": LATITUDE,
        "start": f"{YEAR}0101",
        "end": f"{YEAR}1231",
        "format": "JSON",
        "time-standard": "UTC",
    }
    response = session.get(NASA_POWER_HOURLY_URL, params=params, timeout=180)
    response.raise_for_status()
    return response.json()


def build_weather_frames(nasa_payload: dict) -> Tuple[pd.DataFrame, pd.DataFrame]:
    parameters = nasa_payload["properties"]["parameter"]
    wind_map: Dict[str, float] = parameters["WS10M"]
    solar_map: Dict[str, float] = parameters["ALLSKY_SFC_SW_DWN"]

    timestamps = pd.to_datetime(sorted(wind_map.keys()), format="%Y%m%d%H", utc=True)
    if len(timestamps) != 8760:
        raise ValueError(f"Expected 8760 hourly timestamps for {YEAR}, found {len(timestamps)}")

    wind_series = pd.Series([wind_map[key] for key in sorted(wind_map.keys())], index=timestamps)
    solar_series = pd.Series([solar_map[key] for key in sorted(solar_map.keys())], index=timestamps)

    wind_df = pd.DataFrame(
        {
            "timestamp": timestamps.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "location_name": REPRESENTATIVE_LOCATION,
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "wind_speed_10m_m_per_s": wind_series.to_numpy(),
            "source": "NASA POWER Hourly API",
            "source_dataset": "MERRA-2 via NASA POWER",
            "time_standard": "UTC",
        }
    )

    solar_df = pd.DataFrame(
        {
            "timestamp": timestamps.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "location_name": REPRESENTATIVE_LOCATION,
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "solar_radiation_kw_per_m2": solar_series.to_numpy() / 1000.0,
            "raw_allsky_sfc_sw_dwn_wh_per_m2": solar_series.to_numpy(),
            "source": "NASA POWER Hourly API",
            "source_dataset": "SYN1DEG/MERRA-2 via NASA POWER",
            "time_standard": "UTC",
        }
    )

    return wind_df, solar_df


def write_weather_note(decision: WeatherSourceDecision, nasa_payload: dict) -> None:
    units = nasa_payload["parameters"]
    lines = [
        "# Weather Source Note",
        "",
        f"- Target case: Santiago island, represented by a point near Praia at `{decision.latitude:.2f}, {decision.longitude:.2f}`.",
        "- Reason for point choice: Praia is the island's main demand center and provides a transparent, reproducible representative point for a first workbook run.",
        f"- Renewables.ninja attempted first: `{decision.renewables_ninja_status}`.",
        f"- Renewables.ninja message: `{decision.renewables_ninja_message}`.",
        "- Renewables.ninja could not provide 2023 hourly data for this run, so it was used only as the first-choice check, not as the final weather source.",
        f"- Final weather source used: `{decision.fallback_source}`.",
        "- Wind series used: `WS10M` from NASA POWER in m/s at 10 m height, aligned to UTC.",
        "- Solar series used: `ALLSKY_SFC_SW_DWN` from NASA POWER in Wh/m^2 per hour, converted to `kW/m^2` by dividing by 1000 for workbook compatibility.",
        "- Load timestamps already in this project are UTC (`...Z`), so the weather series were also kept in UTC for direct hourly alignment.",
        "- Wind and solar are weather-based proxy inputs for Santiago, not on-island measured plant output data.",
        "",
        "## NASA POWER metadata",
        "",
        f"- Header title: `{nasa_payload['header']['title']}`.",
        f"- API version: `{nasa_payload['header']['api']['version']}`.",
        f"- Source stack: `{', '.join(nasa_payload['header']['sources'])}`.",
        f"- Wind units: `{units['WS10M']['units']}`.",
        f"- Solar units before conversion: `{units['ALLSKY_SFC_SW_DWN']['units']}`.",
    ]
    (PROJECT_DIR / "weather_source_note.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def export_weather() -> None:
    _ensure_dirs()

    ninja_models, ninja_probe_response = try_renewables_ninja_2023()
    (RAW_DIR / "renewables_ninja_models.json").write_text(
        json.dumps(ninja_models, indent=2),
        encoding="utf-8",
    )
    (RAW_DIR / "renewables_ninja_2023_probe.txt").write_text(
        f"status_code={ninja_probe_response.status_code}\n\n{ninja_probe_response.text}",
        encoding="utf-8",
    )

    if ninja_probe_response.ok:
        raise RuntimeError("Renewables.ninja unexpectedly returned 2023 data; the fallback logic should be revisited.")

    nasa_payload = fetch_nasa_power_hourly_2023()
    (RAW_DIR / "nasa_power_santiago_2023_hourly.json").write_text(
        json.dumps(nasa_payload, indent=2),
        encoding="utf-8",
    )

    wind_df, solar_df = build_weather_frames(nasa_payload)
    wind_df.to_csv(PROJECT_DIR / "Santiago_2023_hourly_wind.csv", index=False)
    solar_df.to_csv(PROJECT_DIR / "Santiago_2023_hourly_solar.csv", index=False)

    decision = WeatherSourceDecision(
        primary_source="Renewables.ninja",
        fallback_source="NASA POWER Hourly API",
        renewables_ninja_status=f"HTTP {ninja_probe_response.status_code}",
        renewables_ninja_message=ninja_probe_response.text.strip(),
        latitude=LATITUDE,
        longitude=LONGITUDE,
    )
    write_weather_note(decision, nasa_payload)


if __name__ == "__main__":
    export_weather()
