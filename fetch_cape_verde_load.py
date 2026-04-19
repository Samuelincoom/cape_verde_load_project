from __future__ import annotations

import json
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import requests

BASE_URL = "https://api.electricitymap.org/v3"
PROJECT_ROOT = Path(__file__).resolve().parent
RAW_RESPONSES_DIR = PROJECT_ROOT / "raw_api_responses"
YEAR = 2023
BENCHMARK_GWH = 572.9
HOURLY_CHUNK_DAYS = 10
API_TIMEOUT = (20, 120)
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
ZONE_SEARCH_TERMS = ["santiago", "praia", "cabo verde", "cape verde", "cabo-verde", "cv"]


@dataclass
class ZoneSelection:
    chosen_zone: str
    selection_basis: str
    zone_listing_source: str
    island_level_zone_found: bool
    island_candidates: list[dict[str, Any]]
    country_candidates: list[dict[str, Any]]
    all_zone_rows: list[dict[str, Any]]


def iso_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sanitize_filename(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value)


def ensure_dirs() -> None:
    RAW_RESPONSES_DIR.mkdir(parents=True, exist_ok=True)


def json_default(value: Any) -> Any:
    if isinstance(value, (datetime, pd.Timestamp)):
        return iso_z(value.to_pydatetime() if isinstance(value, pd.Timestamp) else value)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (np.floating, np.integer, np.bool_)):
        return value.item()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=json_default), encoding="utf-8")


def build_session(auth_token: str | None) -> requests.Session:
    session = requests.Session()
    session.headers.update({"Accept": "application/json", "User-Agent": "cape-verde-load-coursework/1.0"})
    if auth_token:
        session.headers["auth-token"] = auth_token
    return session


def request_json(
    session: requests.Session,
    path: str,
    params: dict[str, Any] | None,
    raw_output_path: Path,
    retries: int = 3,
) -> tuple[int | None, Any, dict[str, Any]]:
    url = f"{BASE_URL}{path}"
    params = params or {}
    last_error: str | None = None

    for attempt in range(1, retries + 1):
        request_record: dict[str, Any] = {
            "requested_at_utc": iso_z(datetime.now(timezone.utc)),
            "path": path,
            "url": url,
            "params": params,
            "attempt": attempt,
        }
        try:
            response = session.get(url, params=params, timeout=API_TIMEOUT)
            request_record["status_code"] = response.status_code
            request_record["ok"] = response.ok
            request_record["content_type"] = response.headers.get("Content-Type")
            try:
                payload = response.json()
                request_record["response_json"] = payload
            except ValueError:
                payload = None
                request_record["response_text"] = response.text

            write_json(raw_output_path, request_record)

            if response.status_code in RETRYABLE_STATUS_CODES and attempt < retries:
                time.sleep(2 ** (attempt - 1))
                continue

            return response.status_code, payload, request_record
        except requests.RequestException as exc:
            last_error = str(exc)
            request_record["error"] = last_error
            write_json(raw_output_path, request_record)
            if attempt < retries:
                time.sleep(2 ** (attempt - 1))
                continue

    return None, None, {"path": path, "params": params, "error": last_error}


def coerce_routes(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, dict):
        for candidate_key in ("routes", "authorizedRoutes", "endpoints", "access"):
            candidate = value.get(candidate_key)
            if isinstance(candidate, list):
                return [str(item) for item in candidate]
    return []


def normalize_zone_rows(zones_payload: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    if isinstance(zones_payload, dict):
        items = zones_payload.items()
    elif isinstance(zones_payload, list):
        items = []
        for item in zones_payload:
            if isinstance(item, dict):
                zone_key = str(item.get("zone") or item.get("zoneKey") or item.get("key") or item.get("id") or "")
                items.append((zone_key, item))
    else:
        return rows

    for raw_key, raw_value in items:
        zone_key = str(raw_key or "")
        zone_meta = raw_value if isinstance(raw_value, dict) else {}
        if not zone_key:
            zone_key = str(zone_meta.get("zone") or zone_meta.get("zoneKey") or zone_meta.get("key") or zone_meta.get("id") or "")

        search_blob = json.dumps({"zone_key": zone_key, "payload": raw_value}, ensure_ascii=False).casefold()
        matched_terms = [term for term in ZONE_SEARCH_TERMS if term in search_blob or (term == "cv" and zone_key.upper() == "CV")]

        rows.append(
            {
                "zone_key": zone_key,
                "display_name": zone_meta.get("zoneName")
                or zone_meta.get("name")
                or zone_meta.get("countryName")
                or zone_key,
                "country_name": zone_meta.get("countryName"),
                "matched_terms": matched_terms,
                "matched_search_blob": search_blob,
                "routes": coerce_routes(raw_value),
                "raw_value": raw_value,
            }
        )

    rows.sort(key=lambda row: row["zone_key"])
    return rows


def choose_zone(zone_rows: list[dict[str, Any]]) -> ZoneSelection:
    island_candidates = [
        row
        for row in zone_rows
        if "santiago" in row["matched_search_blob"] or "praia" in row["matched_search_blob"]
    ]
    country_candidates = [
        row
        for row in zone_rows
        if row["zone_key"].upper() == "CV"
        or "cabo verde" in row["matched_search_blob"]
        or "cape verde" in row["matched_search_blob"]
    ]

    if island_candidates:
        island_candidates.sort(
            key=lambda row: (
                0 if "santiago" in row["matched_search_blob"] else 1,
                0 if "praia" in row["matched_search_blob"] else 1,
                row["zone_key"],
            )
        )
        chosen = island_candidates[0]
        return ZoneSelection(
            chosen_zone=chosen["zone_key"],
            selection_basis="Santiago/Praia-specific zone found in /zones response",
            zone_listing_source="authenticated_or_public",
            island_level_zone_found=True,
            island_candidates=island_candidates,
            country_candidates=country_candidates,
            all_zone_rows=zone_rows,
        )

    if country_candidates:
        country_candidates.sort(key=lambda row: (0 if row["zone_key"].upper() == "CV" else 1, row["zone_key"]))
        chosen = country_candidates[0]
        return ZoneSelection(
            chosen_zone=chosen["zone_key"],
            selection_basis="No Santiago/Praia-specific zone found; using country-level Cabo Verde zone",
            zone_listing_source="authenticated_or_public",
            island_level_zone_found=False,
            island_candidates=island_candidates,
            country_candidates=country_candidates,
            all_zone_rows=zone_rows,
        )

    raise RuntimeError("No Cabo Verde-related zone was found in the /zones response for this token.")


def build_zones_summary(
    selection: ZoneSelection,
    zones_payload: Any,
    authenticated_payload: Any,
    public_payload: Any,
) -> str:
    lines: list[str] = [
        "# Electricity Maps Zone Check",
        "",
        f"- Generated: {iso_z(datetime.now(timezone.utc))}",
        f"- Chosen zone: `{selection.chosen_zone}`",
        f"- Decision basis: {selection.selection_basis}",
        f"- Zone listing source used for decision: {selection.zone_listing_source}",
        f"- Santiago/Praia-specific zone found: {'Yes' if selection.island_level_zone_found else 'No'}",
        "",
        "## Search Terms",
        "",
        "- Santiago",
        "- Praia",
        "- Cabo Verde / Cape Verde",
        "- CV",
        "",
        "## Matched Zones",
        "",
        "| zone_key | display_name | matched_terms | routes_visible |",
        "| --- | --- | --- | --- |",
    ]

    matched_rows = [row for row in selection.all_zone_rows if row["matched_terms"]]
    if matched_rows:
        for row in matched_rows:
            routes = ", ".join(row["routes"][:8]) if row["routes"] else "(not listed)"
            matched_terms = ", ".join(row["matched_terms"])
            lines.append(
                f"| `{row['zone_key']}` | {row['display_name']} | {matched_terms} | {routes} |"
            )
    else:
        lines.append("| (none) | (none) | (none) | (none) |")

    lines.extend(
        [
            "",
            "## Raw Payload Type",
            "",
            f"- Decision payload root JSON type: `{type(zones_payload).__name__}`",
            f"- Zone rows normalized: {len(selection.all_zone_rows)}",
            f"- Authenticated /zones empty: {'Yes' if authenticated_payload == {} else 'No'}",
            f"- Public /zones fallback used: {'Yes' if public_payload is not None else 'No'}",
        ]
    )
    return "\n".join(lines) + "\n"


def get_zones(session: requests.Session) -> tuple[Any, ZoneSelection]:
    raw_call_path = RAW_RESPONSES_DIR / "zones_api_call.json"
    status_code, authenticated_payload, _ = request_json(session, "/zones", {"disableCallerLookup": "true"}, raw_call_path)
    if status_code != 200 or authenticated_payload is None:
        raise RuntimeError(f"/zones request failed with status {status_code}.")

    decision_payload = authenticated_payload
    listing_source = "authenticated /zones"
    public_payload = None

    if authenticated_payload == {}:
        public_session = build_session(None)
        public_raw_call_path = RAW_RESPONSES_DIR / "zones_public_api_call.json"
        public_status, public_payload, _ = request_json(
            public_session,
            "/zones",
            {"disableCallerLookup": "true"},
            public_raw_call_path,
        )
        if public_status == 200 and public_payload not in (None, {}):
            decision_payload = public_payload
            listing_source = "public /zones fallback after empty authenticated response"

    zones_raw_output = {
        "authenticated_response": authenticated_payload,
        "public_fallback_response": public_payload,
        "decision_payload_source": listing_source,
        "decision_payload": decision_payload,
    }
    write_json(PROJECT_ROOT / "zones_raw.json", zones_raw_output)

    zone_rows = normalize_zone_rows(decision_payload)
    selection = choose_zone(zone_rows)
    selection.zone_listing_source = listing_source
    summary_md = build_zones_summary(selection, decision_payload, authenticated_payload, public_payload)
    (PROJECT_ROOT / "zones_summary.md").write_text(summary_md, encoding="utf-8")
    return decision_payload, selection


def extract_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in ("data", "history", "results"):
            if isinstance(payload.get(key), list):
                return [item for item in payload[key] if isinstance(item, dict)]
        if "datetime" in payload:
            return [payload]
    return []


def detect_value_key(record: dict[str, Any]) -> str | None:
    preferred_keys = ["load", "totalLoad", "totalReportedLoad", "reportedLoad", "value", "power"]
    for key in preferred_keys:
        if isinstance(record.get(key), (int, float)) and not isinstance(record.get(key), bool):
            return key

    blocked_numeric_keys = {
        "latitude",
        "longitude",
        "lat",
        "lon",
        "capacity",
        "population",
    }
    numeric_keys = [
        key
        for key, value in record.items()
        if isinstance(value, (int, float)) and not isinstance(value, bool) and key not in blocked_numeric_keys
    ]
    if len(numeric_keys) == 1:
        return numeric_keys[0]
    return None


def fetch_chunk(
    session: requests.Session,
    endpoint: str,
    zone: str,
    start: datetime,
    end: datetime,
) -> dict[str, Any]:
    params = {
        "zone": zone,
        "start": iso_z(start),
        "end": iso_z(end),
        "temporalGranularity": "hourly",
        "disableCallerLookup": "true",
    }
    raw_name = f"{sanitize_filename(endpoint.strip('/').replace('/', '__'))}__{sanitize_filename(params['start'])}__{sanitize_filename(params['end'])}.json"
    raw_output_path = RAW_RESPONSES_DIR / raw_name
    status_code, payload, raw_record = request_json(session, endpoint, params, raw_output_path)

    result: dict[str, Any] = {
        "endpoint": endpoint,
        "zone": zone,
        "start": params["start"],
        "end": params["end"],
        "status_code": status_code,
        "raw_output_path": raw_output_path,
        "usable": False,
        "unsupported": False,
        "message": None,
        "records": [],
    }

    if status_code is None:
        result["message"] = raw_record.get("error", "Unknown request failure")
        return result

    if status_code != 200:
        error_text = json.dumps(payload, ensure_ascii=False) if payload is not None else raw_record.get("response_text", "")
        result["message"] = f"HTTP {status_code}: {error_text[:300]}"
        result["unsupported"] = status_code in {400, 401, 403, 404, 405, 422, 501}
        return result

    records = extract_records(payload)
    if not records:
        result["message"] = "200 OK but no time-series records were returned."
        return result

    normalized_records: list[dict[str, Any]] = []
    for record in records:
        timestamp = record.get("datetime") or record.get("timestamp")
        value_key = detect_value_key(record)
        if not timestamp or not value_key:
            continue

        normalized_records.append(
            {
                "timestamp": str(timestamp),
                "zone": str(record.get("zone") or zone),
                "load_value": record.get(value_key),
                "unit": str(record.get("unit") or "MW"),
                "isEstimated": record.get("isEstimated") if "isEstimated" in record else pd.NA,
                "source_endpoint": endpoint,
            }
        )

    if not normalized_records:
        result["message"] = "Records were returned but none contained both a timestamp and a recognizable load value."
        return result

    result["usable"] = True
    result["records"] = normalized_records
    result["message"] = f"Parsed {len(normalized_records)} hourly records."
    return result


def fetch_year(session: requests.Session, zone: str) -> tuple[pd.DataFrame, str, list[dict[str, Any]]]:
    year_start = datetime(YEAR, 1, 1, tzinfo=timezone.utc)
    year_end = datetime(YEAR + 1, 1, 1, tzinfo=timezone.utc)
    endpoints = ["/total-reported-load/past-range", "/total-load/past-range"]
    endpoint_attempt_logs: list[dict[str, Any]] = []

    for endpoint in endpoints:
        all_records: list[dict[str, Any]] = []
        chunk_logs: list[dict[str, Any]] = []
        current_start = year_start
        endpoint_failed = False

        while current_start < year_end:
            current_end = min(current_start + timedelta(days=HOURLY_CHUNK_DAYS), year_end)
            chunk_result = fetch_chunk(session, endpoint, zone, current_start, current_end)
            chunk_logs.append(chunk_result)

            if chunk_result["unsupported"]:
                endpoint_failed = True
                break

            if chunk_result["status_code"] is None:
                raise RuntimeError(f"{endpoint} failed for {chunk_result['start']} to {chunk_result['end']}: {chunk_result['message']}")

            if chunk_result["status_code"] != 200:
                raise RuntimeError(f"{endpoint} returned {chunk_result['status_code']} for {chunk_result['start']} to {chunk_result['end']}: {chunk_result['message']}")

            if chunk_result["usable"]:
                all_records.extend(chunk_result["records"])

            current_start = current_end

        endpoint_attempt_logs.append({"endpoint": endpoint, "chunks": chunk_logs})

        if endpoint_failed:
            continue

        if all_records:
            return pd.DataFrame(all_records), endpoint, endpoint_attempt_logs

    raise RuntimeError("Both hourly load endpoints failed, were unsupported, or returned no usable data.")


def validate_series(df: pd.DataFrame, zone: str, source_endpoint: str) -> tuple[pd.DataFrame, dict[str, Any]]:
    validation: dict[str, Any] = {}
    expected_index = pd.date_range(
        start=f"{YEAR}-01-01T00:00:00Z",
        end=f"{YEAR}-12-31T23:00:00Z",
        freq="h",
        tz="UTC",
    )

    working = df.copy()
    validation["raw_rows_received"] = int(len(working))
    validation["source_endpoint"] = source_endpoint
    validation["zone"] = zone
    validation["expected_rows_for_year"] = int(len(expected_index))

    working["original_timestamp"] = working["timestamp"].astype(str)
    working["timezone_suffix"] = working["original_timestamp"].str.extract(r"(Z|[+-]\d{2}:\d{2})$", expand=False).fillna("naive")
    validation["timezone_suffixes_found"] = sorted(working["timezone_suffix"].dropna().unique().tolist())

    working["timestamp"] = pd.to_datetime(working["timestamp"], utc=True, errors="coerce")
    invalid_timestamps = int(working["timestamp"].isna().sum())
    validation["invalid_timestamps"] = invalid_timestamps
    if invalid_timestamps:
        working = working.dropna(subset=["timestamp"]).copy()

    working["load_value"] = pd.to_numeric(working["load_value"], errors="coerce")
    working["isEstimated"] = working["isEstimated"].astype("boolean")

    duplicates_before = int(working.duplicated(subset=["timestamp"]).sum())
    null_loads_before = int(working["load_value"].isna().sum())
    validation["duplicate_timestamps_before_cleaning"] = duplicates_before
    validation["null_load_values_before_cleaning"] = null_loads_before

    working = working.sort_values(
        by=["timestamp", "load_value", "isEstimated"],
        ascending=[True, False, True],
        na_position="last",
    )
    working = working.drop_duplicates(subset=["timestamp"], keep="first").copy()

    working = working.set_index("timestamp").reindex(expected_index)
    working.index.name = "timestamp"
    working["zone"] = working["zone"].fillna(zone)
    working["unit"] = working["unit"].fillna("MW")
    working["source_endpoint"] = working["source_endpoint"].fillna(source_endpoint)
    working["isEstimated"] = working["isEstimated"].astype("boolean")

    missing_hours = int(working["load_value"].isna().sum())
    estimated_hours = int(working["isEstimated"].fillna(False).sum())
    estimated_share_pct = (estimated_hours / len(working) * 100.0) if len(working) else np.nan
    validation["rows_after_hourly_reindex"] = int(len(working))
    validation["missing_hours_after_cleaning"] = missing_hours
    validation["estimated_hours"] = estimated_hours
    validation["estimated_share_pct"] = estimated_share_pct
    validation["non_estimated_hours"] = int((working["isEstimated"] == False).sum())
    validation["has_8760_rows"] = bool(len(working) == 8760)
    validation["duplicate_timestamps_after_cleaning"] = int(working.index.duplicated().sum())
    validation["null_load_values_after_cleaning"] = missing_hours
    validation["timezone_consistency"] = (
        "Consistent UTC-style timestamps" if set(validation["timezone_suffixes_found"]) <= {"Z", "+00:00"} else "Mixed or non-UTC timestamp suffixes detected"
    )

    annual_total_mwh = float(working["load_value"].sum(skipna=True))
    annual_total_gwh = annual_total_mwh / 1000.0
    benchmark_delta_gwh = annual_total_gwh - BENCHMARK_GWH
    benchmark_delta_pct = (benchmark_delta_gwh / BENCHMARK_GWH) * 100.0 if BENCHMARK_GWH else np.nan
    validation["annual_total_mwh"] = annual_total_mwh
    validation["annual_total_gwh"] = annual_total_gwh
    validation["benchmark_gwh"] = BENCHMARK_GWH
    validation["benchmark_delta_gwh"] = benchmark_delta_gwh
    validation["benchmark_delta_pct"] = benchmark_delta_pct

    if source_endpoint == "/total-reported-load/past-range":
        if estimated_hours == 0:
            data_source_classification = "real reported load from the Electricity Maps API"
        else:
            data_source_classification = "real reported-load endpoint from the Electricity Maps API, with some Electricity Maps estimated hours"
    else:
        if estimated_hours == len(working):
            data_source_classification = "real Electricity Maps processed total-load endpoint, but all hours are estimated rather than directly reported"
        else:
            data_source_classification = "real Electricity Maps processed total-load endpoint, with a mix of measured and estimated hours"
    validation["data_source_classification"] = data_source_classification

    cleaning_steps = [
        "Parsed API timestamps to timezone-aware UTC datetimes.",
        "Sorted rows by timestamp, preferring non-null and non-estimated values when duplicate timestamps existed.",
        "Dropped duplicate timestamps after sorting.",
        "Reindexed to the full 2023 hourly scaffold (8760 hours) and left missing load values blank instead of inventing replacements.",
        "Did not smooth, interpolate, or otherwise alter real API load values.",
    ]
    validation["cleaning_steps"] = cleaning_steps

    if estimated_hours == len(working) and source_endpoint == "/total-load/past-range":
        suitability = "Suitable for academic coursework only with explicit caveats: it is a real Electricity Maps API series, but for Cabo Verde in 2023 it comes from the processed total-load endpoint and every hour is estimated rather than directly reported."
    elif missing_hours == 0 and source_endpoint == "/total-reported-load/past-range":
        suitability = "Strong for academic coursework on the chosen Electricity Maps zone, with the usual caveat that any hours flagged isEstimated are model-assisted rather than directly measured."
    elif missing_hours == 0 and source_endpoint == "/total-load/past-range":
        suitability = "Reasonably strong for academic coursework, but this is processed flow-traced total load rather than directly reported load."
    else:
        suitability = "Usable with caution for academic coursework, but the missing-hour count should be discussed explicitly in the write-up."
    validation["coursework_suitability"] = suitability

    cleaned = working.reset_index().rename(columns={"index": "timestamp"})
    cleaned["timestamp"] = cleaned["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    cleaned = cleaned[["timestamp", "zone", "load_value", "unit", "isEstimated", "source_endpoint"]]
    return cleaned, validation


def build_santiago_proxy(
    cabo_verde_df: pd.DataFrame,
    population_share: float = 0.56,
    base_load_adjustment: float = 0.05,
    seasonality_strength: float = 0.10,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    working = cabo_verde_df.copy()
    working["timestamp_dt"] = pd.to_datetime(working["timestamp"], utc=True)
    working["load_value"] = pd.to_numeric(working["load_value"], errors="coerce")

    annual_mean = float(working["load_value"].mean(skipna=True))
    scaled = working["load_value"] * population_share
    baseline = population_share * annual_mean * base_load_adjustment
    proxy_load = scaled * (1 - base_load_adjustment) + baseline

    monthly_mean = working.groupby(working["timestamp_dt"].dt.month)["load_value"].mean()
    month_factor = monthly_mean / annual_mean if annual_mean else monthly_mean * np.nan
    seasonal_multiplier = 1 + seasonality_strength * (working["timestamp_dt"].dt.month.map(month_factor) - 1)
    proxy_load = proxy_load * seasonal_multiplier

    target_total = float(scaled.sum(skipna=True))
    modeled_total = float(proxy_load.sum(skipna=True))
    if modeled_total and not np.isnan(modeled_total):
        proxy_load = proxy_load * (target_total / modeled_total)

    proxy_df = pd.DataFrame(
        {
            "timestamp": working["timestamp"],
            "zone": "SANTIAGO_PROXY_FROM_CV",
            "load_value": proxy_load,
            "unit": "MW",
            "proxy_status": "modeled_not_measured",
            "source_shape_zone": working["zone"],
            "population_share_assumption": population_share,
            "base_load_adjustment": base_load_adjustment,
            "seasonality_strength": seasonality_strength,
        }
    )

    proxy_meta = {
        "population_share_assumption": population_share,
        "base_load_adjustment": base_load_adjustment,
        "seasonality_strength": seasonality_strength,
        "proxy_annual_total_mwh": float(proxy_df["load_value"].sum(skipna=True)),
        "proxy_annual_total_gwh": float(proxy_df["load_value"].sum(skipna=True) / 1000.0),
    }
    return proxy_df, proxy_meta


def write_validation_markdown(
    validation: dict[str, Any],
    island_level_zone_found: bool,
    chosen_zone: str,
) -> None:
    direct_benchmark_note = (
        "The 572.9 GWh benchmark is directly comparable because the chosen zone is country-level Cabo Verde."
        if chosen_zone.upper() == "CV"
        else "The 572.9 GWh benchmark is a national Cabo Verde reference only and is not directly comparable to a sub-national island/city zone."
    )

    lines = [
        "# Cabo Verde 2023 Validation Note",
        "",
        f"- Generated: {iso_z(datetime.now(timezone.utc))}",
        f"- Santiago exists as a separate zone: {'Yes' if island_level_zone_found else 'No'}",
        f"- Chosen zone: `{chosen_zone}`",
        f"- Endpoint used: `{validation['source_endpoint']}`",
        f"- Data source classification: {validation['data_source_classification']}",
        f"- Estimated hours: {validation['estimated_hours']}",
        f"- Estimated share: {validation['estimated_share_pct']:.2f}%",
        f"- Annual total: {validation['annual_total_mwh']:.3f} MWh ({validation['annual_total_gwh']:.3f} GWh)",
        f"- Missing hours after cleaning: {validation['missing_hours_after_cleaning']}",
        f"- Duplicate timestamps before cleaning: {validation['duplicate_timestamps_before_cleaning']}",
        f"- Null load values after cleaning: {validation['null_load_values_after_cleaning']}",
        f"- Timezone consistency: {validation['timezone_consistency']} ({', '.join(validation['timezone_suffixes_found'])})",
        f"- 8760-row result achieved: {'Yes' if validation['has_8760_rows'] else 'No'}",
        f"- External benchmark used: {validation['benchmark_gwh']:.1f} GWh",
        f"- Benchmark delta: {validation['benchmark_delta_gwh']:.3f} GWh ({validation['benchmark_delta_pct']:.2f}%)",
        f"- Benchmark interpretation: {direct_benchmark_note}",
        f"- Academic suitability: {validation['coursework_suitability']}",
        "",
        "## Cleaning Steps",
        "",
    ]
    if validation.get("zone_fetch_note"):
        lines.insert(6, f"- Zone access note: {validation['zone_fetch_note']}")
    lines.extend([f"- {step}" for step in validation["cleaning_steps"]])
    (PROJECT_ROOT / "CaboVerde_2023_validation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_proxy_method_markdown(proxy_meta: dict[str, Any], chosen_zone: str) -> None:
    lines = [
        "# Santiago Proxy Method",
        "",
        "This file describes a modeled Santiago hourly load proxy. It is not measured Santiago data.",
        "",
        f"- Generated: {iso_z(datetime.now(timezone.utc))}",
        f"- Source shape zone: `{chosen_zone}`",
        f"- Population share assumption: {proxy_meta['population_share_assumption']:.2%}",
        f"- Base-load adjustment: {proxy_meta['base_load_adjustment']:.2%}",
        f"- Seasonality strength: {proxy_meta['seasonality_strength']:.2%}",
        f"- Proxy annual total: {proxy_meta['proxy_annual_total_mwh']:.3f} MWh ({proxy_meta['proxy_annual_total_gwh']:.3f} GWh)",
        "",
        "## Method",
        "",
        "- Step 1: start from the real Cabo Verde hourly shape returned by Electricity Maps.",
        "- Step 2: scale each hour by a transparent Santiago population-share assumption.",
        "- Step 3: apply a simple base-load adjustment by pulling each hourly value 5% toward a flat annual mean component.",
        "- Step 4: apply a transparent seasonality adjustment derived from the real Cabo Verde monthly pattern, with only a modest 10% amplification of monthly deviations from the annual mean.",
        "- Step 5: renormalize the modeled series so its annual total still matches the population-share-scaled Cabo Verde annual total.",
        "",
        "## Interpretation",
        "",
        "- This proxy is modeled, not measured.",
        "- It should be treated as a sensitivity or coursework approximation for Santiago when no separate Santiago/Praia Electricity Maps zone is available.",
        "- It is suitable for transparent exploratory academic use, but not as a substitute for a metered Santiago system-load time series.",
    ]
    (PROJECT_ROOT / "Santiago_proxy_method.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def export_outputs(
    cleaned_df: pd.DataFrame,
    validation: dict[str, Any],
    chosen_zone: str,
    chosen_endpoint: str,
    island_level_zone_found: bool,
    proxy_df: pd.DataFrame | None = None,
    proxy_meta: dict[str, Any] | None = None,
) -> None:
    cleaned_csv_path = PROJECT_ROOT / "CaboVerde_2023_hourly_load_clean.csv"
    excel_path = PROJECT_ROOT / "CaboVerde_2023_hourly_load.xlsx"

    cleaned_df.to_csv(cleaned_csv_path, index=False)
    write_validation_markdown(validation, island_level_zone_found, chosen_zone)

    metadata_rows = [
        {"field": "date_created_utc", "value": iso_z(datetime.now(timezone.utc))},
        {"field": "chosen_zone", "value": chosen_zone},
        {"field": "chosen_endpoint", "value": chosen_endpoint},
        {"field": "data_type", "value": "reported_load" if chosen_endpoint == "/total-reported-load/past-range" else "processed_total_load"},
        {"field": "data_source_classification", "value": validation["data_source_classification"]},
        {"field": "contains_estimated_hours", "value": bool(validation["estimated_hours"] > 0)},
        {"field": "estimated_hours", "value": validation["estimated_hours"]},
        {"field": "estimated_share_pct", "value": validation["estimated_share_pct"]},
        {"field": "benchmark_gwh", "value": BENCHMARK_GWH},
        {"field": "santiago_zone_available", "value": island_level_zone_found},
    ]
    metadata_df = pd.DataFrame(metadata_rows)

    validation_sheet_df = pd.DataFrame(
        [{"field": key, "value": value if not isinstance(value, list) else "; ".join(map(str, value))} for key, value in validation.items()]
    )

    with pd.ExcelWriter(excel_path, engine="xlsxwriter") as writer:
        cleaned_df.to_excel(writer, sheet_name="Data", index=False)
        validation_sheet_df.to_excel(writer, sheet_name="Validation", index=False)
        metadata_df.to_excel(writer, sheet_name="Metadata", index=False)
        if proxy_df is not None:
            proxy_df.to_excel(writer, sheet_name="SantiagoProxy", index=False)

        for sheet_name, dataframe in {
            "Data": cleaned_df,
            "Validation": validation_sheet_df,
            "Metadata": metadata_df,
            **({"SantiagoProxy": proxy_df} if proxy_df is not None else {}),
        }.items():
            worksheet = writer.sheets[sheet_name]
            for column_index, column_name in enumerate(dataframe.columns):
                max_width = max(len(str(column_name)), dataframe[column_name].astype(str).map(len).max()) + 2
                worksheet.set_column(column_index, column_index, min(max_width, 30))

    if proxy_df is not None and proxy_meta is not None:
        proxy_df.to_csv(PROJECT_ROOT / "Santiago_2023_proxy_hourly_load.csv", index=False)
        write_proxy_method_markdown(proxy_meta, chosen_zone)


def main() -> int:
    os.chdir(PROJECT_ROOT)
    ensure_dirs()

    auth_token = os.environ.get("ELECTRICITY_MAPS_TOKEN")
    if not auth_token:
        print("ELECTRICITY_MAPS_TOKEN environment variable is required.", file=sys.stderr)
        return 1

    session = build_session(auth_token)
    _, zone_selection = get_zones(session)

    if not zone_selection.island_level_zone_found:
        print("No Santiago/Praia-specific Electricity Maps zone was found. Proceeding with country-level Cabo Verde zone and then building a clearly labeled Santiago proxy.")

    effective_zone = zone_selection.chosen_zone
    zone_fetch_note: str | None = None
    try:
        year_df, chosen_endpoint, endpoint_logs = fetch_year(session, effective_zone)
    except RuntimeError as exc:
        if zone_selection.island_level_zone_found and zone_selection.country_candidates:
            fallback_zone = zone_selection.country_candidates[0]["zone_key"]
            if fallback_zone != effective_zone:
                zone_fetch_note = (
                    f"Preferred island/city zone `{effective_zone}` could not be fetched with the provided token; "
                    f"fell back to `{fallback_zone}`. Original error: {exc}"
                )
                effective_zone = fallback_zone
                year_df, chosen_endpoint, endpoint_logs = fetch_year(session, effective_zone)
            else:
                raise
        else:
            raise

    write_json(PROJECT_ROOT / "fetch_attempt_log.json", endpoint_logs)

    cleaned_df, validation = validate_series(year_df, effective_zone, chosen_endpoint)
    if zone_fetch_note:
        validation["zone_fetch_note"] = zone_fetch_note

    proxy_df: pd.DataFrame | None = None
    proxy_meta: dict[str, Any] | None = None
    if not zone_selection.island_level_zone_found:
        proxy_df, proxy_meta = build_santiago_proxy(cleaned_df)

    export_outputs(
        cleaned_df=cleaned_df,
        validation=validation,
        chosen_zone=effective_zone,
        chosen_endpoint=chosen_endpoint,
        island_level_zone_found=zone_selection.island_level_zone_found,
        proxy_df=proxy_df,
        proxy_meta=proxy_meta,
    )

    print(f"Chosen zone: {effective_zone}")
    print(f"Chosen endpoint: {chosen_endpoint}")
    print(f"Annual total: {validation['annual_total_gwh']:.3f} GWh")
    print(f"Estimated hours: {validation['estimated_hours']}")
    if proxy_meta is not None:
        print(f"Santiago proxy annual total: {proxy_meta['proxy_annual_total_gwh']:.3f} GWh")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
