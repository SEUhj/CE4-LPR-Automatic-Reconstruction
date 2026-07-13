# Evaluation annotations

This directory contains the interval annotations used to evaluate valid-trace segment detection.

## File naming

- manualYYYY.csv: manually interpreted reference intervals.
- autoYYYY.csv: intervals produced by the proposed method.

The YYYY suffix identifies the year used by scripts/evaluate_iou.py. The script accepts a custom year list and file prefixes.

## CSV format

Each CSV file contains two integer columns with no header:

    start,end

Indices are zero-based trace indices. Both start and end are inclusive. The metric implementation converts each interval to a binary trace mask using the range start through end.

These are interval-level manual annotations of valid radar-trace segments, rather than pixel-level two-dimensional image masks. They are sufficient to reproduce the IOU, precision, recall, F1, accuracy, and segment-matching calculations.

## Reproduce the evaluation

From the repository root:

    $env:PYTHONPATH = "src"
    python scripts/evaluate_iou.py --data-dir data_iou --output outputs/iou_metrics.csv

The original Chang'e-4 .2B files are not redistributed here. Their official source and the filenames used in the study are documented in the root README.
