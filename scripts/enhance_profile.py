from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from ce4_lpr.preprocess import agc_gain, average_trace_removal, bandpass_filter, dc_remove, time_zero_alignment


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Enhance a reconstructed LPR radargram saved as .npy.")
    parser.add_argument("--input", required=True, help="Input .npy file produced by run_reconstruction.py.")
    parser.add_argument("--output", required=True, help="Output .npy path.")
    parser.add_argument("--fs", type=float, required=True, help="Sampling frequency in Hz for bandpass filtering.")
    parser.add_argument("--low", type=float, default=150e6, help="Bandpass low cutoff in Hz.")
    parser.add_argument("--high", type=float, default=900e6, help="Bandpass high cutoff in Hz.")
    parser.add_argument("--agc-window", type=int, default=101, help="AGC window length in samples.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = np.load(args.input)
    enhanced = time_zero_alignment(data)
    enhanced = dc_remove(enhanced)
    enhanced = bandpass_filter(enhanced, fs=args.fs, low=args.low, high=args.high)
    enhanced = average_trace_removal(enhanced)
    enhanced = agc_gain(enhanced, window=args.agc_window)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    np.save(args.output, enhanced.astype(np.float32))
    print(f"Enhanced radargram saved to {args.output}")


if __name__ == "__main__":
    main()
