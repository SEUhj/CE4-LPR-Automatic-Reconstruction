from __future__ import annotations

import numpy as np
from scipy.ndimage import median_filter, uniform_filter1d
from scipy.signal import butter, filtfilt


def time_zero_alignment(data: np.ndarray, search_rows: int = 300) -> np.ndarray:
    """Align each trace by the strongest early-time arrival."""
    data = np.asarray(data, dtype=float)
    aligned = np.zeros_like(data)
    refs = np.argmax(np.abs(data[:search_rows, :]), axis=0)
    target = int(np.median(refs))
    for col, ref in enumerate(refs):
        aligned[:, col] = np.roll(data[:, col], target - int(ref))
    return aligned


def dc_remove(data: np.ndarray) -> np.ndarray:
    return np.asarray(data, dtype=float) - np.mean(data, axis=0, keepdims=True)


def bandpass_filter(data: np.ndarray, fs: float, low: float = 150e6, high: float = 900e6, order: int = 4) -> np.ndarray:
    nyq = 0.5 * fs
    b, a = butter(order, [low / nyq, high / nyq], btype="band")
    return filtfilt(b, a, data, axis=0)


def average_trace_removal(data: np.ndarray) -> np.ndarray:
    return np.asarray(data, dtype=float) - np.mean(data, axis=1, keepdims=True)


def denoise_2d_median(data: np.ndarray, size: tuple[int, int] = (3, 3)) -> np.ndarray:
    return median_filter(data, size=size)


def agc_gain(data: np.ndarray, window: int = 101, eps: float = 1e-8) -> np.ndarray:
    energy = uniform_filter1d(np.asarray(data, dtype=float) ** 2, size=window, axis=0, mode="nearest")
    gained = data / np.sqrt(energy + eps)
    scale = np.percentile(np.abs(gained), 99)
    return gained / scale if scale > 0 else gained
