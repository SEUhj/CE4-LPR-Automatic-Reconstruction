# Automatic Reconstruction of Sparse Lunar Penetrating Radar Data

This repository contains the cleaned open-source code for:

**Automatic Reconstruction of Sparse Lunar Penetrating Radar Data from Chang'e-4 Rover**

The reusable implementation is split into a small Python package under `src/ce4_lpr`, with two notebooks for running the reconstruction workflow and displaying the evaluation results.

## Data Sources and Scope

All Chang'e-4 LPR data used in this study are from China's Lunar and Planetary Data Release System:

<http://moon.bao.ac.cn/>

This repository does not redistribute the fully preprocessed Chang'e-4 dataset or the original `.2B` radar files. Users can download Chang'e-4 LPR data from the official data portal and process the raw `.2B` files with this algorithm to obtain valid-segment reconstruction results.

The test data used in the paper correspond to the following Chang'e-4 LPR source files:

- `CE4_GRAS_LPR-2B_SCI_N_20221118015001_20221119050500_0267_A.2B`
- `CE4_GRAS_LPR-2B_SCI_N_20221119073501_20221119112000_0268_A.2B`
- `CE4_GRAS_LPR-2B_SCI_N_20221127102001_20221128110000_0270_A.2B`

Please download the required Chang'e-4 LPR files from the official data portal:

<http://moon.bao.ac.cn/>

The `data_iou/` folder provides the segment CSV files used for quantitative checking in this open-source package:

- `manual*.csv`: manually interpreted valid-segment intervals.
- `auto*.csv`: valid-segment intervals produced by the proposed method.

These CSV files contain segment interval indices rather than original radar data. The manual interval files can also be used as index files to extract valid data sections from officially downloaded Chang'e-4 LPR data.

## Baseline Reference

The baseline mentioned in the paper is based on the code by G. Roncoroni et al.:

[Giacomo-Roncoroni/LPR_CE4](https://github.com/Giacomo-Roncoroni/LPR_CE4)

This repository focuses on releasing the proposed method and the associated segment-level evaluation files. Baseline comparison data and scripts are not included here. Users who wish to reproduce the baseline comparison should refer to the original baseline repository and apply it to the same official Chang'e-4 LPR data.

## Repository Layout

- `src/ce4_lpr/io.py`: Chang'e LPR `.2B` reader for CH-2B high-frequency and CH-1 low-frequency files.
- `src/ce4_lpr/corrupt.py`: corrupted-trace detection and stability-weighted bilateral correction.
- `src/ce4_lpr/reconstruction.py`: automatic depth truncation, Sobel-X, IsoData thresholding, and morphological segment refinement.
- `src/ce4_lpr/preprocess.py`: optional enhancement utilities for geological interpretation.
- `src/ce4_lpr/metrics.py`: IOU, precision, recall, F1, segment matching, and yearly evaluation.
- `scripts/run_reconstruction.py`: run the full reconstruction workflow on downloaded `.2B` files.
- `scripts/evaluate_iou.py`: evaluate the detected segment CSV files against manual labels.
- `scripts/enhance_profile.py`: apply the optional image-enhancement chain to a reconstructed `.npy` radargram.
- `data_iou/`: manual labels (`manual*.csv`) and proposed-method results (`auto*.csv`).

## Installation

```bash
pip install -r requirements.txt
```

Alternatively, create the Conda environment:

```bash
conda env create -f environment.yml
conda activate ce4-lpr
```

When running scripts from this repository without installing the package, set `PYTHONPATH`:

```powershell
$env:PYTHONPATH = "src"
```

## Quick Start

Recommended notebook entry points:

```text
notebooks/01_run_reconstruction.ipynb
notebooks/02_iou_results.ipynb
```

Run the reconstruction workflow on downloaded Chang'e-4 `.2B` files:

```powershell
$env:PYTHONPATH = "src"
python scripts/run_reconstruction.py --input-dir "path/to/downloaded_ce4_lpr_files" --output-dir outputs/reconstruction
```

Evaluate the proposed method against manual labels:

```powershell
$env:PYTHONPATH = "src"
python scripts/evaluate_iou.py --data-dir data_iou
```

Optionally enhance a reconstructed radargram for interpretation:

```powershell
$env:PYTHONPATH = "src"
python scripts/enhance_profile.py --input outputs/reconstruction/reconstructed_valid_data.npy --output outputs/reconstruction/enhanced.npy --fs 2.5e9
```

## Notes

The calibrated default parameters follow the manuscript:

- split row for corrupted-trace detection: `300`
- threshold scaling factor: `1.6`
- short-segment removal threshold: `10` traces
- gap-fill threshold: `30` traces
- minimum final segment length: `20` traces

The submission version no longer depends on notebook execution order. Generated outputs are written to `outputs/`.

## Citation

If you use this code or the provided segment-level evaluation files in your research, please cite the original paper:

**Automatic Reconstruction of Sparse Lunar Penetrating Radar Data from Chang'e-4 Rover**

This paper is currently under publication processing. Full citation information, including the DOI, will be added once the paper is formally published.
