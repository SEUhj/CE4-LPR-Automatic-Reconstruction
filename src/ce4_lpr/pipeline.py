from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .corrupt import CorruptTraceConfig, detect_and_repair_corrupt_traces
from .io import read_lpr_folder
from .reconstruction import SegmentConfig, automatic_depth_cut, detect_valid_segments, extract_segments, sobel_x_after_cut, trace_variance


@dataclass(frozen=True)
class ReconstructionConfig:
    corrupt: CorruptTraceConfig = CorruptTraceConfig()
    segment: SegmentConfig = SegmentConfig()


def run_reconstruction(input_dir: str | Path, output_dir: str | Path, config: ReconstructionConfig | None = None) -> dict[str, object]:
    """Run the complete sparse valid-segment reconstruction workflow."""
    cfg = config or ReconstructionConfig()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    raw, boundaries, files = read_lpr_folder(input_dir)
    repair = detect_and_repair_corrupt_traces(raw, cfg.corrupt)
    cut_idx = automatic_depth_cut(repair.repaired, cfg.segment.threshold_ratio, cfg.segment.depth_buffer)
    sobel_data = sobel_x_after_cut(repair.repaired, cut_idx)
    variances = trace_variance(sobel_data)
    segments, thresholds, mask = detect_valid_segments(sobel_data, boundaries, cfg.segment)
    reconstructed, remapped_bad = extract_segments(repair.repaired, segments, repair.bad_indices)

    np.save(output_dir / "reconstructed_valid_data.npy", reconstructed.astype(np.float32))
    np.save(output_dir / "repaired_full_data.npy", repair.repaired.astype(np.float32))
    np.savez(
        output_dir / "diagnostics.npz",
        bad_indices=repair.bad_indices,
        remapped_bad_indices=np.asarray(remapped_bad, dtype=int),
        preliminary_mask=repair.preliminary_mask,
        released_by_coherence=repair.released_by_coherence,
        thresholds=np.asarray(thresholds, dtype=float),
        variances=variances,
        final_mask=mask,
        boundaries=np.asarray(boundaries, dtype=int),
        cut_idx=np.asarray([cut_idx], dtype=int),
    )
    pd.DataFrame(segments, columns=["start", "end"]).to_csv(output_dir / "detected_segments.csv", index=False, header=False)
    pd.DataFrame({"file": [str(p) for p in files], "start": boundaries[:-1], "end": boundaries[1:]}).to_csv(
        output_dir / "source_files.csv", index=False
    )

    return {
        "raw_shape": raw.shape,
        "reconstructed_shape": reconstructed.shape,
        "n_segments": len(segments),
        "n_bad_traces": int(repair.bad_indices.size),
        "cut_idx": int(cut_idx),
        "output_dir": str(output_dir),
    }
