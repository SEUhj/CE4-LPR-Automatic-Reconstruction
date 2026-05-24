from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class LprFormat:
    name: str
    record_len: int
    samples: int
    echo_offset: int = 114


CH2B = LprFormat("Channel 2B high frequency (~500 MHz)", 8307, 2048)
CH1 = LprFormat("Channel 1 low frequency (~60 MHz)", 32883, 8192)
KNOWN_FORMATS = (CH2B, CH1)


def detect_lpr_format(path: str | Path) -> LprFormat:
    """Detect Chang'e LPR binary format from file size."""
    path = Path(path)
    file_size = path.stat().st_size
    for fmt in KNOWN_FORMATS:
        if file_size % fmt.record_len == 0:
            return fmt
    raise ValueError(f"Unsupported LPR file structure: {path.name} ({file_size} bytes)")


def read_lpr_file(path: str | Path) -> np.ndarray:
    """Read a Chang'e LPR .2B file as a samples x traces float32 matrix."""
    path = Path(path)
    fmt = detect_lpr_format(path)
    echo_bytes = fmt.samples * 4

    raw = np.fromfile(path, dtype=np.uint8)
    n_records = raw.size // fmt.record_len
    records = raw.reshape(n_records, fmt.record_len)
    echo = records[:, fmt.echo_offset : fmt.echo_offset + echo_bytes]
    return np.ascontiguousarray(echo).view("<f4").T


def read_lpr_folder(folder: str | Path) -> tuple[np.ndarray, list[int], list[Path]]:
    """Read and concatenate all .2B files in a folder.

    Returns the concatenated data, trace boundaries for each source file, and
    the accepted file list.
    """
    folder = Path(folder)
    files = sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".2b")
    if not files:
        raise FileNotFoundError(f"No .2B files found in {folder}")

    data_parts: list[np.ndarray] = []
    boundaries = [0]
    expected_samples: int | None = None
    accepted: list[Path] = []

    for path in files:
        data = read_lpr_file(path)
        if expected_samples is None:
            expected_samples = data.shape[0]
        if data.shape[0] != expected_samples:
            continue
        data_parts.append(data)
        accepted.append(path)
        boundaries.append(boundaries[-1] + data.shape[1])

    if not data_parts:
        raise ValueError(f"No compatible .2B files could be read from {folder}")
    return np.concatenate(data_parts, axis=1), boundaries, accepted
