from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from fetch_cape_verde_load import build_santiago_proxy

PROJECT_ROOT = Path(__file__).resolve().parent
SOURCE_CSV = PROJECT_ROOT / "CaboVerde_2023_hourly_load_clean.csv"
SOURCE_XLSX = PROJECT_ROOT / "CaboVerde_2023_hourly_load.xlsx"
TARGET_ANNUAL_GWH = 572.9
TARGET_ANNUAL_MWH = TARGET_ANNUAL_GWH * 1000.0

CALIBRATED_CV_CSV = PROJECT_ROOT / "CaboVerde_2023_hourly_load_calibrated.csv"
CALIBRATED_CV_XLSX = PROJECT_ROOT / "CaboVerde_2023_hourly_load_calibrated.xlsx"
CALIBRATED_SANTIAGO_CSV = PROJECT_ROOT / "Santiago_2023_proxy_hourly_load_calibrated.csv"
CALIBRATED_SANTIAGO_XLSX = PROJECT_ROOT / "Santiago_2023_proxy_hourly_load_calibrated.xlsx"
METHOD_NOTE = PROJECT_ROOT / "CaboVerde_2023_calibration_method.md"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_source_dataframe() -> pd.DataFrame:
    if SOURCE_CSV.exists():
        return pd.read_csv(SOURCE_CSV)
    if SOURCE_XLSX.exists():
        return pd.read_excel(SOURCE_XLSX, sheet_name="Data")
    raise FileNotFoundError("Neither the calibrated source CSV nor the XLSX input file exists in the project folder.")


def calibrate_national_series(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    working = df.copy()
    working["load_value"] = pd.to_numeric(working["load_value"], errors="coerce")

    if working["load_value"].isna().any():
        raise ValueError("The source file contains null or non-numeric load values and cannot be calibrated uniformly.")

    original_total_mwh = float(working["load_value"].sum())
    original_total_gwh = original_total_mwh / 1000.0
    scaling_factor = TARGET_ANNUAL_MWH / original_total_mwh

    working["load_value"] = working["load_value"] * scaling_factor

    last_valid_index = working["load_value"].last_valid_index()
    if last_valid_index is None:
        raise ValueError("No valid load values were found in the source file.")

    residual_mwh = TARGET_ANNUAL_MWH - float(working["load_value"].sum())
    working.loc[last_valid_index, "load_value"] = working.loc[last_valid_index, "load_value"] + residual_mwh

    calibrated_total_mwh = float(working["load_value"].sum())
    calibrated_total_gwh = calibrated_total_mwh / 1000.0

    metadata = {
        "created_utc": utc_now_iso(),
        "source_file_used": SOURCE_CSV.name if SOURCE_CSV.exists() else SOURCE_XLSX.name,
        "original_annual_total_mwh": original_total_mwh,
        "original_annual_total_gwh": original_total_gwh,
        "target_annual_total_mwh": TARGET_ANNUAL_MWH,
        "target_annual_total_gwh": TARGET_ANNUAL_GWH,
        "scaling_factor": scaling_factor,
        "residual_adjustment_mwh": residual_mwh,
        "calibrated_annual_total_mwh": calibrated_total_mwh,
        "calibrated_annual_total_gwh": calibrated_total_gwh,
        "hourly_rows": int(len(working)),
        "cabo_verde_status": "estimated_not_reported",
        "santiago_status": "proxy_not_measured",
    }
    return working, metadata


def autosize_worksheet(writer: pd.ExcelWriter, sheet_name: str, dataframe: pd.DataFrame) -> None:
    worksheet = writer.sheets[sheet_name]
    for column_index, column_name in enumerate(dataframe.columns):
        max_width = max(len(str(column_name)), dataframe[column_name].astype(str).map(len).max()) + 2
        worksheet.set_column(column_index, column_index, min(max_width, 32))


def resolve_excel_engine() -> str:
    try:
        from xlsxwriter import Workbook  # type: ignore

        _ = Workbook
        return "xlsxwriter"
    except Exception:
        return "openpyxl"


def export_excel(path: Path, data_df: pd.DataFrame, method_df: pd.DataFrame, metadata_df: pd.DataFrame) -> None:
    engine = resolve_excel_engine()
    with pd.ExcelWriter(path, engine=engine) as writer:
        data_df.to_excel(writer, sheet_name="Data", index=False)
        method_df.to_excel(writer, sheet_name="Method", index=False)
        metadata_df.to_excel(writer, sheet_name="Metadata", index=False)
        if engine == "xlsxwriter":
            autosize_worksheet(writer, "Data", data_df)
            autosize_worksheet(writer, "Method", method_df)
            autosize_worksheet(writer, "Metadata", metadata_df)


def write_method_note(metadata: dict[str, Any]) -> None:
    lines = [
        "# Cabo Verde 2023 Calibration Method",
        "",
        f"- Created: {metadata['created_utc']}",
        f"- Source file used: `{metadata['source_file_used']}`",
        f"- Original annual total: {metadata['original_annual_total_mwh']:.6f} MWh ({metadata['original_annual_total_gwh']:.3f} GWh)",
        f"- Target annual total: {metadata['target_annual_total_mwh']:.1f} MWh ({metadata['target_annual_total_gwh']:.1f} GWh)",
        f"- Calibrated annual total achieved: {metadata['calibrated_annual_total_mwh']:.6f} MWh ({metadata['calibrated_annual_total_gwh']:.3f} GWh)",
        f"- Scaling factor applied uniformly to every hourly Cabo Verde load value: {metadata['scaling_factor']:.12f}",
        f"- Residual adjustment on the final hour to hit the exact target total: {metadata['residual_adjustment_mwh']:.12f} MWh",
        "- Cabo Verde data status: estimated, not reported.",
        "- Santiago data status: proxy, not measured.",
        "",
        "## Interpretation",
        "",
        "- The calibrated Cabo Verde series preserves the original hourly shape and changes only the scale.",
        "- The regenerated Santiago proxy uses the calibrated national hourly shape as its starting point.",
        "- The Santiago file remains a modeled proxy and should not be treated as measured island demand.",
    ]
    METHOD_NOTE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_method_dataframe(metadata: dict[str, Any]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"item": "created_utc", "value": metadata["created_utc"]},
            {"item": "source_file_used", "value": metadata["source_file_used"]},
            {"item": "original_annual_total_gwh", "value": metadata["original_annual_total_gwh"]},
            {"item": "target_annual_total_gwh", "value": metadata["target_annual_total_gwh"]},
            {"item": "calibrated_annual_total_gwh", "value": metadata["calibrated_annual_total_gwh"]},
            {"item": "scaling_factor", "value": metadata["scaling_factor"]},
            {"item": "residual_adjustment_mwh", "value": metadata["residual_adjustment_mwh"]},
            {"item": "cabo_verde_status", "value": metadata["cabo_verde_status"]},
            {"item": "santiago_status", "value": metadata["santiago_status"]},
        ]
    )


def build_metadata_dataframe(metadata: dict[str, Any], label: str) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"field": "dataset_label", "value": label},
            {"field": "created_utc", "value": metadata["created_utc"]},
            {"field": "hourly_rows", "value": metadata["hourly_rows"]},
            {"field": "original_annual_total_mwh", "value": metadata["original_annual_total_mwh"]},
            {"field": "target_annual_total_mwh", "value": metadata["target_annual_total_mwh"]},
            {"field": "calibrated_annual_total_mwh", "value": metadata["calibrated_annual_total_mwh"]},
            {"field": "scaling_factor", "value": metadata["scaling_factor"]},
        ]
    )


def main() -> int:
    source_df = load_source_dataframe()
    calibrated_df, metadata = calibrate_national_series(source_df)

    calibrated_df.to_csv(CALIBRATED_CV_CSV, index=False, float_format="%.12f")
    calibrated_proxy_df, proxy_meta = build_santiago_proxy(calibrated_df)
    calibrated_proxy_df.to_csv(CALIBRATED_SANTIAGO_CSV, index=False, float_format="%.12f")

    method_df = build_method_dataframe(metadata)
    cv_metadata_df = build_metadata_dataframe(metadata, "Cabo Verde calibrated hourly load")
    santiago_metadata_df = build_metadata_dataframe(metadata, "Santiago calibrated proxy hourly load")
    santiago_metadata_df.loc[len(santiago_metadata_df)] = {
        "field": "proxy_annual_total_mwh",
        "value": proxy_meta["proxy_annual_total_mwh"],
    }
    santiago_metadata_df.loc[len(santiago_metadata_df)] = {
        "field": "proxy_annual_total_gwh",
        "value": proxy_meta["proxy_annual_total_gwh"],
    }

    export_excel(CALIBRATED_CV_XLSX, calibrated_df, method_df, cv_metadata_df)
    export_excel(CALIBRATED_SANTIAGO_XLSX, calibrated_proxy_df, method_df, santiago_metadata_df)
    write_method_note(metadata)

    print(f"Original annual total: {metadata['original_annual_total_gwh']:.3f} GWh")
    print(f"Scaling factor: {metadata['scaling_factor']:.12f}")
    print(f"Calibrated annual total: {metadata['calibrated_annual_total_gwh']:.3f} GWh")
    print(f"Calibrated Santiago proxy annual total: {proxy_meta['proxy_annual_total_gwh']:.3f} GWh")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
