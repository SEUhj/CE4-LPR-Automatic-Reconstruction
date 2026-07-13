from __future__ import annotations

import argparse
import json
from pathlib import Path

from ce4_lpr.corrupt import CorruptTraceConfig
from ce4_lpr.pipeline import ReconstructionConfig, run_reconstruction
from ce4_lpr.reconstruction import SegmentConfig


def load_config(path: Path | None) -> ReconstructionConfig:
    if path is None:
        return ReconstructionConfig()
    payload = json.loads(path.read_text(encoding="utf-8"))
    return ReconstructionConfig(
        corrupt=CorruptTraceConfig(**payload.get("corrupt", {})),
        segment=SegmentConfig(**payload.get("segment", {})),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run sparse Chang'e LPR valid-segment reconstruction.")
    parser.add_argument("--input-dir", required=True, help="Directory containing .2B files.")
    parser.add_argument("--output-dir", default="outputs/reconstruction", help="Directory for generated results.")
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Optional JSON configuration file. Omit to use the dataclass defaults.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    summary = run_reconstruction(Path(args.input_dir), Path(args.output_dir), config)
    print("Reconstruction complete")
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
