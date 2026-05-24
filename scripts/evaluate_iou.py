from __future__ import annotations

import argparse
from pathlib import Path

from ce4_lpr.metrics import evaluate_years


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate detected segments against manual labels.")
    parser.add_argument("--data-dir", default="data_iou", help="Directory containing year CSV files.")
    parser.add_argument("--years", nargs="+", type=int, default=[2019, 2020, 2021, 2022, 2023, 2024])
    parser.add_argument("--pred-prefix", default="auto", help="Prediction CSV prefix, e.g. auto2019.csv.")
    parser.add_argument("--ref-prefix", default="manual", help="Reference CSV prefix, e.g. manual2019.csv.")
    parser.add_argument("--output", default="", help="Optional CSV path for the metric table.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = evaluate_years(Path(args.data_dir), args.years, args.pred_prefix, args.ref_prefix)
    print(result.to_string(index=False))
    if args.output:
        result.to_csv(args.output, index=False)


if __name__ == "__main__":
    main()
