from __future__ import annotations

from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP

import numpy as np
import pandas as pd


def load_segments_csv(path: str | Path) -> pd.DataFrame:
    """Load two-column segment CSV and normalize columns to start/end."""
    path = Path(path)
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame(columns=["start", "end"])
    df = pd.read_csv(path, header=None, usecols=[0, 1], names=["start", "end"])
    return df.dropna().astype(int)


def segments_to_mask(segments: pd.DataFrame, total_length: int) -> np.ndarray:
    mask = np.zeros(total_length, dtype=np.uint8)
    for _, row in segments.iterrows():
        start = max(0, min(int(row["start"]), total_length))
        end = max(0, min(int(row["end"]) + 1, total_length))
        if start < end:
            mask[start:end] = 1
    return mask


def point_metrics(mask_gt: np.ndarray, mask_pred: np.ndarray) -> dict[str, float | int]:
    gt = mask_gt > 0
    pred = mask_pred > 0
    tp = int(np.sum(gt & pred))
    fp = int(np.sum(~gt & pred))
    fn = int(np.sum(gt & ~pred))
    tn = int(np.sum(~gt & ~pred))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    iou = tp / (tp + fp + fn) if tp + fp + fn else 0.0
    f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0
    accuracy = (tp + tn) / len(gt) if len(gt) else 0.0
    return {
        "IOU": round(iou, 4),
        "Precision": round(precision, 4),
        "Recall": round(recall, 4),
        "F1_Score": round(f1, 4),
        "Accuracy": round(accuracy, 4),
        "TP_points": tp,
        "FP_points": fp,
        "FN_points": fn,
    }


def count_matching_intervals(reference: pd.DataFrame, predicted: pd.DataFrame) -> int:
    if reference.empty or predicted.empty:
        return 0
    matched = 0
    for _, row in reference.iterrows():
        overlap = predicted[(predicted["start"] <= row["end"]) & (predicted["end"] >= row["start"])]
        if not overlap.empty:
            matched += 1
    return matched


def evaluate_years(data_dir: str | Path, years: list[int], pred_prefix: str = "auto", ref_prefix: str = "manual") -> pd.DataFrame:
    rows = []
    data_dir = Path(data_dir)
    for year in years:
        ref = load_segments_csv(data_dir / f"{ref_prefix}{year}.csv")
        pred = load_segments_csv(data_dir / f"{pred_prefix}{year}.csv")
        if ref.empty and pred.empty:
            continue
        total_length = int(max(ref["end"].max() if not ref.empty else 0, pred["end"].max() if not pred.empty else 0)) + 100
        metrics = point_metrics(segments_to_mask(ref, total_length), segments_to_mask(pred, total_length))
        matched = count_matching_intervals(ref, pred)
        rows.append(
            {
                "Year": year,
                **metrics,
                "Manual_Count": len(ref),
                "Pred_Count": len(pred),
                "Matched_Segments": matched,
                "Segment_Recall": round(matched / len(ref), 4) if len(ref) else 0.0,
                "Count_Diff": len(pred) - len(ref),
            }
        )
    return pd.DataFrame(rows)


def round_half_up(value: float, ndigits: int = 4) -> float:
    quant = Decimal("1").scaleb(-ndigits)
    return float(Decimal(str(value)).quantize(quant, rounding=ROUND_HALF_UP))


def mean_round_half_up(values: pd.Series, ndigits: int = 4, scale: Decimal | int | str = 1) -> float:
    decimals = [Decimal(str(v)) for v in values]
    mean_value = (sum(decimals) / Decimal(len(decimals))) * Decimal(str(scale))
    quant = Decimal("1").scaleb(-ndigits)
    return float(mean_value.quantize(quant, rounding=ROUND_HALF_UP))


def phase_summary(metrics_df: pd.DataFrame) -> pd.DataFrame:
    """Summarize metrics using the calibration/test grouping used in the paper."""
    phases = [
        ("Calibration (2019-2022)", metrics_df[metrics_df["Year"].between(2019, 2022)]),
        ("Test Set (2023-2024)", metrics_df[metrics_df["Year"].between(2023, 2024)]),
        ("All Chang'e-4 (2019-2024)", metrics_df),
    ]
    rows = []
    for phase, df in phases:
        if df.empty:
            continue
        rows.append(
            {
                "Phase": phase,
                "Avg_Precision": mean_round_half_up(df["Precision"], 4),
                "Avg_Recall": mean_round_half_up(df["Recall"], 4),
                "Avg_IOU": mean_round_half_up(df["IOU"], 4),
                "Avg_F1": mean_round_half_up(df["F1_Score"], 4),
                "Total_Count_Error": int(df["Count_Diff"].sum()),
            }
        )
    return pd.DataFrame(rows)
