from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.ndimage import sobel


@dataclass(frozen=True)
class SegmentConfig:
    threshold_ratio: float = 0.1
    depth_buffer: int = 50
    threshold_scale: float = 1.6
    min_noise_len: int = 10
    max_gap_fill: int = 30
    min_final_len: int = 20


def automatic_depth_cut(data: np.ndarray, ratio: float = 0.1, buffer: int = 50) -> int:
    """Find the depth where near-surface energy decays, then add a safety buffer."""
    mean_amp = np.mean(np.abs(data), axis=1)
    peak_idx = int(np.argmax(mean_amp))
    peak = float(mean_amp[peak_idx])
    cut_idx = data.shape[0] - 1
    for idx in range(peak_idx, data.shape[0]):
        if mean_amp[idx] < peak * ratio:
            cut_idx = idx
            break
    return min(cut_idx + buffer, data.shape[0] - 10)


def sobel_x_after_cut(data: np.ndarray, cut_idx: int) -> np.ndarray:
    """Apply horizontal Sobel operator below the automatic depth cut."""
    return sobel(np.asarray(data[cut_idx:, :], dtype=float), axis=1, mode="nearest")


def isodata_threshold(values: np.ndarray, scale: float = 1.6, max_iter: int = 100, tol: float = 1e-5) -> float:
    """Ridler-Calvard/IsoData threshold in log-variance domain."""
    values = np.asarray(values, dtype=float)
    if values.size == 0 or np.nanmax(values) < 1e-12:
        return 0.0
    log_values = np.log1p(values)
    threshold = float(np.nanmean(log_values))
    prev = -np.inf
    for _ in range(max_iter):
        if abs(threshold - prev) < tol:
            break
        prev = threshold
        bg = log_values[log_values < threshold]
        fg = log_values[log_values >= threshold]
        mean_bg = float(bg.mean()) if bg.size else 0.0
        mean_fg = float(fg.mean()) if fg.size else threshold
        threshold = 0.5 * (mean_bg + mean_fg)
    return float(np.expm1(threshold) * scale)


def _mask_runs(mask: np.ndarray) -> list[tuple[int, int]]:
    """Return true runs as half-open intervals [start, stop)."""
    padded = np.r_[False, np.asarray(mask, dtype=bool), False]
    edges = np.diff(padded.astype(int))
    starts = np.flatnonzero(edges == 1)
    ends = np.flatnonzero(edges == -1)
    return [(int(s), int(e)) for s, e in zip(starts, ends)]


def mask_to_segments(mask: np.ndarray, offset: int = 0, min_len: int = 1) -> list[tuple[int, int]]:
    """Return segments using the legacy notebook right-boundary convention.

    The original notebook stored the right edge detected by ``edges == -1`` and
    later sliced with ``end + 1``. That convention keeps one boundary trace on
    the right side of each detected segment, so it is preserved here for
    reproducibility with the submitted notebook results.
    """
    return [(offset + s, offset + e) for s, e in _mask_runs(mask) if e - s >= min_len]


def refine_mask(mask: np.ndarray, cfg: SegmentConfig) -> np.ndarray:
    """Remove short detections, fill small gaps, and enforce final segment length."""
    mask_clean = np.asarray(mask, dtype=bool).copy()
    for start, stop in _mask_runs(mask_clean):
        if stop - start < cfg.min_noise_len:
            mask_clean[start:stop] = False

    inv = ~mask_clean
    for start, stop in _mask_runs(inv):
        if start == 0 or stop == mask_clean.size:
            continue
        if stop - start <= cfg.max_gap_fill:
            mask_clean[start:stop] = True

    final_mask = np.zeros_like(mask_clean)
    for start, stop in _mask_runs(mask_clean):
        if stop - start >= cfg.min_final_len:
            final_mask[start:stop] = True
    return final_mask


def detect_valid_segments(
    sobel_data: np.ndarray,
    boundaries: list[int],
    cfg: SegmentConfig | None = None,
) -> tuple[list[tuple[int, int]], list[float], np.ndarray]:
    """Detect valid trace segments independently for each source file."""
    cfg = cfg or SegmentConfig()
    variances = np.var(np.asarray(sobel_data, dtype=float), axis=0)
    all_segments: list[tuple[int, int]] = []
    thresholds: list[float] = []
    final_mask = np.zeros_like(variances, dtype=bool)

    for start, end in zip(boundaries[:-1], boundaries[1:]):
        local_var = variances[start:end]
        threshold = isodata_threshold(local_var, cfg.threshold_scale)
        thresholds.append(threshold)
        if threshold <= 0:
            continue
        local_mask = refine_mask(local_var >= threshold, cfg)
        final_mask[start:end] = local_mask
        all_segments.extend(mask_to_segments(local_mask, offset=start, min_len=cfg.min_final_len))
    return all_segments, thresholds, final_mask


def trace_variance(sobel_data: np.ndarray) -> np.ndarray:
    """Return trace-wise variance from Sobel-X data."""
    return np.var(np.asarray(sobel_data, dtype=float), axis=0)


def extract_segments(data: np.ndarray, segments: list[tuple[int, int]], bad_indices: np.ndarray | None = None) -> tuple[np.ndarray, list[int]]:
    """Extract valid segments and report repaired-bad-trace positions in the concatenated output."""
    if not segments:
        return np.empty((data.shape[0], 0), dtype=data.dtype), []

    bad_set = set(map(int, bad_indices if bad_indices is not None else []))
    parts = []
    remapped_bad: list[int] = []
    offset = 0
    for start, end in segments:
        parts.append(data[:, start : end + 1])
        for col in range(start, end + 1):
            if col in bad_set:
                remapped_bad.append(offset + col - start)
        offset += end - start + 1
    return np.concatenate(parts, axis=1), remapped_bad
