from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from scipy.ndimage import gaussian_filter1d, median_filter
from scipy.stats import pearsonr


RepairMethod = Literal["none", "linear", "nearest", "stbi"]


@dataclass(frozen=True)
class CorruptTraceConfig:
    split_row: int = 300
    block_size: int = 500
    trend_sigma: float = 200.0
    width_factor: float = 12.0
    coherence_threshold: float = 0.95
    coherence_samples: int = 500
    stability_power: float = 2.0


@dataclass
class CorruptTraceResult:
    repaired: np.ndarray
    bad_indices: np.ndarray
    shallow_mask: np.ndarray
    deep_mask: np.ndarray
    nan_mask: np.ndarray
    preliminary_mask: np.ndarray
    released_by_coherence: np.ndarray


@dataclass
class CorruptTraceDetection:
    bad_indices: np.ndarray
    shallow_mask: np.ndarray
    deep_mask: np.ndarray
    nan_mask: np.ndarray
    preliminary_mask: np.ndarray
    released_by_coherence: np.ndarray


def macro_trend_checker(
    energy: np.ndarray,
    block_size: int = 500,
    trend_sigma: float = 200.0,
    width_factor: float = 12.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Detect anomalous traces using local dynamic thresholds in log-energy space."""
    energy = np.asarray(energy, dtype=float)
    n = energy.size
    eps = 1e-10
    valid = ~np.isnan(energy)
    filled = energy.copy()
    filled[~valid] = np.median(energy[valid]) if np.any(valid) else 1.0

    log_energy = np.log10(filled + eps)
    large_win = min(max(3, int(n * 0.02)), 51)
    if large_win % 2 == 0:
        large_win += 1

    trend = median_filter(log_energy, size=large_win, mode="reflect")
    trend = gaussian_filter1d(trend, sigma=trend_sigma)
    residuals = log_energy - trend

    local_sigmas = np.zeros(n, dtype=float)
    for start in range(0, n, block_size):
        stop = min(start + block_size, n)
        block = residuals[start:stop]
        q75, q25 = np.percentile(block, [75, 25])
        iqr = q75 - q25
        local_sigmas[start:stop] = iqr / 1.349 if iqr > 0 else np.std(block)

    local_sigmas = gaussian_filter1d(local_sigmas, sigma=block_size / 2)
    median_sigma = float(np.median(local_sigmas))
    if median_sigma > 0:
        local_sigmas = np.maximum(local_sigmas, median_sigma * 0.5)

    upper = 10 ** (trend + width_factor * local_sigmas)
    lower = 10 ** (trend - width_factor * local_sigmas)
    with np.errstate(invalid="ignore"):
        mask = (energy > upper) | (energy < lower)
    mask[np.isnan(energy)] = True
    return mask, upper, lower


def trace_stability(trace: np.ndarray, split_row: int = 300) -> float:
    deep_energy = float(np.sum(np.nan_to_num(np.asarray(trace[split_row:], dtype=float)) ** 2))
    return 1.0 / (deep_energy + 1e-8)


def refine_bad_traces_with_coherence(
    data: np.ndarray,
    candidate_mask: np.ndarray,
    pcc_threshold: float = 0.95,
    coherence_samples: int = 500,
) -> tuple[np.ndarray, np.ndarray]:
    """Release candidate bad traces that remain highly coherent with the left neighbor."""
    final_mask = np.asarray(candidate_mask, dtype=bool).copy()
    released = np.zeros_like(final_mask)
    test_len = min(coherence_samples, data.shape[0])

    for idx in np.flatnonzero(candidate_mask):
        if idx <= 0 or idx >= data.shape[1] - 1 or np.any(np.isnan(data[:, idx])):
            continue

        trace_curr = np.nan_to_num(data[:test_len, idx])
        trace_left = np.nan_to_num(data[:test_len, idx - 1])
        if np.std(trace_curr) <= 0 or np.std(trace_left) <= 0:
            continue

        coef, _ = pearsonr(trace_curr, trace_left)
        if coef > pcc_threshold:
            final_mask[idx] = False
            released[idx] = True

    return final_mask, released


def detect_corrupt_traces(
    data: np.ndarray,
    config: CorruptTraceConfig | None = None,
) -> CorruptTraceDetection:
    """Detect corrupted traces without modifying the input data."""
    cfg = config or CorruptTraceConfig()
    data_float = np.asarray(data, dtype=float)
    split = min(cfg.split_row, data_float.shape[0])

    shallow_energy = np.sum(data_float[:split, :] ** 2, axis=0)
    deep_energy = np.sum(data_float[split:, :] ** 2, axis=0)
    shallow_mask, _, _ = macro_trend_checker(shallow_energy, cfg.block_size, cfg.trend_sigma, cfg.width_factor)
    deep_mask, _, _ = macro_trend_checker(deep_energy, cfg.block_size, cfg.trend_sigma, cfg.width_factor)
    nan_mask = np.any(np.isnan(data_float), axis=0)

    preliminary_mask = shallow_mask | deep_mask | nan_mask
    bad_mask, released_by_coherence = refine_bad_traces_with_coherence(
        data_float,
        preliminary_mask,
        pcc_threshold=cfg.coherence_threshold,
        coherence_samples=cfg.coherence_samples,
    )
    bad_indices = np.flatnonzero(bad_mask)

    return CorruptTraceDetection(
        bad_indices,
        shallow_mask,
        deep_mask,
        nan_mask,
        preliminary_mask,
        released_by_coherence,
    )


def repair_corrupt_traces(
    data: np.ndarray,
    bad_indices: np.ndarray,
    config: CorruptTraceConfig | None = None,
    method: RepairMethod = "stbi",
) -> np.ndarray:
    """Repair known bad traces using one of the ablation interpolation methods."""
    if method not in {"none", "linear", "nearest", "stbi"}:
        raise ValueError(f"Unsupported corrupt-trace repair method: {method}")

    cfg = config or CorruptTraceConfig()
    data_float = np.asarray(data, dtype=float)
    repaired = data_float.copy()
    bad_indices = np.unique(np.asarray(bad_indices, dtype=int))
    if method == "none" or bad_indices.size == 0:
        return repaired

    all_indices = np.arange(data_float.shape[1])
    good_indices = np.setdiff1d(all_indices, bad_indices)
    if good_indices.size == 0:
        return repaired

    split = min(cfg.split_row, data_float.shape[0])

    for bad_col in bad_indices:
        if bad_col < 0 or bad_col >= data_float.shape[1]:
            raise IndexError(f"Bad-trace index out of bounds: {bad_col}")
        left = good_indices[good_indices < bad_col]
        right = good_indices[good_indices > bad_col]
        left_idx = int(left[-1]) if left.size else None
        right_idx = int(right[0]) if right.size else None

        if left_idx is not None and right_idx is not None:
            if method == "nearest":
                source_idx = left_idx if bad_col - left_idx <= right_idx - bad_col else right_idx
                repaired[:, bad_col] = repaired[:, source_idx]
            else:
                w_dist_l = 1.0 / (bad_col - left_idx)
                w_dist_r = 1.0 / (right_idx - bad_col)
                if method == "stbi":
                    w_l = w_dist_l * trace_stability(repaired[:, left_idx], split) ** cfg.stability_power
                    w_r = w_dist_r * trace_stability(repaired[:, right_idx], split) ** cfg.stability_power
                else:
                    w_l, w_r = w_dist_l, w_dist_r
                repaired[:, bad_col] = (w_l * repaired[:, left_idx] + w_r * repaired[:, right_idx]) / (w_l + w_r)
        elif left_idx is not None:
            repaired[:, bad_col] = repaired[:, left_idx]
        elif right_idx is not None:
            repaired[:, bad_col] = repaired[:, right_idx]

    return repaired


def detect_and_repair_corrupt_traces(
    data: np.ndarray,
    config: CorruptTraceConfig | None = None,
) -> CorruptTraceResult:
    """Detect corrupted traces and repair them with stability-weighted bilateral interpolation."""
    cfg = config or CorruptTraceConfig()
    detection = detect_corrupt_traces(data, cfg)
    repaired = repair_corrupt_traces(data, detection.bad_indices, cfg, method="stbi")
    return CorruptTraceResult(
        repaired,
        detection.bad_indices,
        detection.shallow_mask,
        detection.deep_mask,
        detection.nan_mask,
        detection.preliminary_mask,
        detection.released_by_coherence,
    )


def detect_and_repair_corrupt_traces_by_boundaries(
    data: np.ndarray,
    boundaries: list[int],
    config: CorruptTraceConfig | None = None,
) -> CorruptTraceResult:
    """Detect and repair traces independently within each source sub-file."""
    data_float = np.asarray(data, dtype=float)
    if data_float.ndim != 2:
        raise ValueError("data must be a samples-by-traces matrix")
    if not boundaries or boundaries[0] != 0 or boundaries[-1] != data_float.shape[1]:
        raise ValueError("boundaries must span all traces in data")

    repaired = data_float.copy()
    masks = {
        "shallow": np.zeros(data_float.shape[1], dtype=bool),
        "deep": np.zeros(data_float.shape[1], dtype=bool),
        "nan": np.zeros(data_float.shape[1], dtype=bool),
        "preliminary": np.zeros(data_float.shape[1], dtype=bool),
        "released": np.zeros(data_float.shape[1], dtype=bool),
    }
    all_bad_indices: list[int] = []

    for start, end in zip(boundaries[:-1], boundaries[1:]):
        if start >= end:
            raise ValueError("Each sub-file boundary interval must contain at least one trace")
        local_result = detect_and_repair_corrupt_traces(data_float[:, start:end], config)
        repaired[:, start:end] = local_result.repaired
        all_bad_indices.extend((local_result.bad_indices + start).tolist())
        masks["shallow"][start:end] = local_result.shallow_mask
        masks["deep"][start:end] = local_result.deep_mask
        masks["nan"][start:end] = local_result.nan_mask
        masks["preliminary"][start:end] = local_result.preliminary_mask
        masks["released"][start:end] = local_result.released_by_coherence

    return CorruptTraceResult(
        repaired,
        np.asarray(all_bad_indices, dtype=int),
        masks["shallow"],
        masks["deep"],
        masks["nan"],
        masks["preliminary"],
        masks["released"],
    )
