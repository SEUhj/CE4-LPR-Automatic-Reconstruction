from __future__ import annotations

import argparse
from pathlib import Path

from ce4_lpr.pipeline import ReconstructionConfig, run_reconstruction


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run sparse Chang'e LPR valid-segment reconstruction.")
    parser.add_argument("--input-dir", required=True, help="Directory containing .2B files.")
    parser.add_argument("--output-dir", default="outputs/reconstruction", help="Directory for generated results.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run_reconstruction(Path(args.input_dir), Path(args.output_dir), ReconstructionConfig())
    print("Reconstruction complete")
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
