# Automatic Reconstruction of Sparse Lunar Penetrating Radar Data

This repository contains the cleaned open-source code for:

**Automatic Reconstruction of Sparse Lunar Penetrating Radar Data from Chang'e-4 Rover**

The reusable implementation is a Python package under src/ce4_lpr, together with notebooks and command-line scripts for reconstruction and evaluation.

## Data sources and scope

All Chang'e-4 LPR data used in this study are from China's Lunar and Planetary Data Release System:

http://moon.bao.ac.cn/

The raw mission files are not redistributed here. Download the required Chang'e-4 high-frequency LPR .2B files from the official portal and place them in data_raw/ before running the workflow.

The test data used in the paper correspond to:

- CE4_GRAS_LPR-2B_SCI_N_20221118015001_20221119050500_0267_A.2B
- CE4_GRAS_LPR-2B_SCI_N_20221119073501_20221119112000_0268_A.2B
- CE4_GRAS_LPR-2B_SCI_N_20221127102001_20221128110000_0270_A.2B

The data_iou/ directory contains the interval annotations and automatic results used for quantitative evaluation. See data_iou/README.md for the exact format.

## Reproducibility release

The reproducibility configuration is stored in configs/reproduction_config.json and is consumed by scripts/run_reconstruction.py. It records all corruption-detection and segment-refinement parameters used by the workflow.

The versioned reproducibility release is v1.0.0. Cite this release together with the full commit hash in the paper. The raw source files remain available from the official data portal rather than this repository.

## Runtime environment

The supported environment is specified in environment.yml:

- Conda environment name: ce4-lpr
- Python: 3.11
- Channel: conda-forge
- Dependencies: NumPy, pandas, SciPy, Matplotlib, tqdm, Jupyter, and Notebook

A pip-compatible dependency list is provided in requirements.txt.

## Repository layout

- src/ce4_lpr/io.py: Chang'e LPR .2B reader.
- src/ce4_lpr/corrupt.py: corrupted-trace detection and stability-weighted bilateral repair.
- src/ce4_lpr/reconstruction.py: depth truncation, Sobel-X, IsoData thresholding, and segment refinement.
- src/ce4_lpr/preprocess.py: optional enhancement utilities.
- src/ce4_lpr/metrics.py: IOU, precision, recall, F1, and segment matching.
- scripts/run_reconstruction.py: complete reconstruction workflow.
- scripts/evaluate_iou.py: evaluation against manual intervals.
- configs/reproduction_config.json: reproducibility parameters.
- data_iou/: manual interval labels and automatic results.
- data_raw/: place official downloaded .2B files here.

## Installation

    pip install -r requirements.txt

Alternatively:

    conda env create -f environment.yml
    conda activate ce4-lpr

When running without installing the package, set PYTHONPATH:

    $env:PYTHONPATH = "src"

## Quick start

First download the three source files listed above and place them in data_raw/.

    $env:PYTHONPATH = "src"
    python scripts/run_reconstruction.py --input-dir data_raw --output-dir outputs/reconstruction --config configs/reproduction_config.json

Outputs are written to outputs/reconstruction/, including reconstructed arrays, diagnostics, source-file boundaries, and detected segment intervals.

Evaluate the supplied annotations and automatic results:

    $env:PYTHONPATH = "src"
    python scripts/evaluate_iou.py --data-dir data_iou --output outputs/iou_metrics.csv

Optional enhancement:

    $env:PYTHONPATH = "src"
    python scripts/enhance_profile.py --input outputs/reconstruction/reconstructed_valid_data.npy --output outputs/reconstruction/enhanced.npy --fs 2.5e9

## Default calibrated parameters

The values in configs/reproduction_config.json follow the manuscript:

- split row for corrupted-trace detection: 300
- block size: 500
- trend sigma: 200
- width factor: 12
- coherence threshold: 0.95
- coherence samples: 500
- stability power: 2
- depth threshold ratio: 0.1
- depth buffer: 50
- threshold scaling factor: 1.6
- short-segment removal threshold: 10 traces
- gap-fill threshold: 30 traces
- minimum final segment length: 20 traces

## Annotation and data availability

The manual files manualYYYY.csv are reference annotations of valid trace intervals. Each row contains two integer columns, start and end, without a header. Indices are zero-based and both endpoints are inclusive. These are interval-level annotations, not pixel-level two-dimensional image masks, and are sufficient to reproduce the IOU, precision, recall, F1, accuracy, and segment-matching metrics.

The corresponding autoYYYY.csv files contain the proposed-method results. The exact raw source filenames and download instructions are provided above. This arrangement avoids redistributing the mission data while preserving reproducible evaluation inputs.

## Baseline reference

The baseline mentioned in the paper is based on:

https://github.com/Giacomo-Roncoroni/LPR_CE4

Baseline comparison data and scripts are not included here.

## Citation

Machine-readable citation metadata is provided in CITATION.cff. If you use this code or the evaluation annotations, cite the associated paper and the versioned GitHub release.
# Automatic Reconstruction of Sparse Lunar Penetrating Radar Data

This repository contains the cleaned open-source code for:

**Automatic Reconstruction of Sparse Lunar Penetrating Radar Data from Chang'e-4 Rover**

The reusable implementation is a Python package under src/ce4_lpr, together with notebooks and command-line scripts for reconstruction and evaluation.

## Data sources and scope

All Chang'e-4 LPR data used in this study are from China's Lunar and Planetary Data Release System:

http://moon.bao.ac.cn/

The raw mission files are not redistributed here. Download the required Chang'e-4 high-frequency LPR .2B files from the official portal and place them in data_raw/ before running the workflow.

The test data used in the paper correspond to:

- CE4_GRAS_LPR-2B_SCI_N_20221118015001_20221119050500_0267_A.2B
- CE4_GRAS_LPR-2B_SCI_N_20221119073501_20221119112000_0268_A.2B
- CE4_GRAS_LPR-2B_SCI_N_20221127102001_20221128110000_0270_A.2B

The data_iou/ directory contains the interval annotations and automatic results used for quantitative evaluation. See data_iou/README.md for the exact format.

## Reproducibility release

The reproducibility configuration is stored in configs/reproduction_config.json and is consumed by scripts/run_reconstruction.py. It records all corruption-detection and segment-refinement parameters used by the workflow.

After the final manuscript version is frozen, create a GitHub release named v1.0.0 from the final commit and cite both the release and its full commit hash in the paper. The raw source files remain available from the official data portal rather than this repository.

## Runtime environment

The supported environment is specified in environment.yml:

- Conda environment name: ce4-lpr
- Python: 3.11
- Channel: conda-forge
- Dependencies: NumPy, pandas, SciPy, Matplotlib, tqdm, Jupyter, and Notebook

A pip-compatible dependency list is provided in requirements.txt.

## Repository layout

- src/ce4_lpr/io.py: Chang'e LPR .2B reader.
- src/ce4_lpr/corrupt.py: corrupted-trace detection and stability-weighted bilateral repair.
- src/ce4_lpr/reconstruction.py: depth truncation, Sobel-X, IsoData thresholding, and segment refinement.
- src/ce4_lpr/preprocess.py: optional enhancement utilities.
- src/ce4_lpr/metrics.py: IOU, precision, recall, F1, and segment matching.
- scripts/run_reconstruction.py: complete reconstruction workflow.
- scripts/evaluate_iou.py: evaluation against manual intervals.
- configs/reproduction_config.json: reproducibility parameters.
- data_iou/: manual interval labels and automatic results.
- data_raw/: place official downloaded .2B files here.

## Installation

    pip install -r requirements.txt

Alternatively:

    conda env create -f environment.yml
    conda activate ce4-lpr

When running without installing the package, set PYTHONPATH:

    $env:PYTHONPATH = "src"

## Quick start

First download the three source files listed above and place them in data_raw/.

    $env:PYTHONPATH = "src"
    python scripts/run_reconstruction.py --input-dir data_raw --output-dir outputs/reconstruction --config configs/reproduction_config.json

Outputs are written to outputs/reconstruction/, including reconstructed arrays, diagnostics, source-file boundaries, and detected segment intervals.

Evaluate the supplied annotations and automatic results:

    $env:PYTHONPATH = "src"
    python scripts/evaluate_iou.py --data-dir data_iou --output outputs/iou_metrics.csv

Optional enhancement:

    $env:PYTHONPATH = "src"
    python scripts/enhance_profile.py --input outputs/reconstruction/reconstructed_valid_data.npy --output outputs/reconstruction/enhanced.npy --fs 2.5e9

## Default calibrated parameters

The values in configs/reproduction_config.json follow the manuscript:

- split row for corrupted-trace detection: 300
- block size: 500
- trend sigma: 200
- width factor: 12
- coherence threshold: 0.95
- coherence samples: 500
- stability power: 2
- depth threshold ratio: 0.1
- depth buffer: 50
- threshold scaling factor: 1.6
- short-segment removal threshold: 10 traces
- gap-fill threshold: 30 traces
- minimum final segment length: 20 traces

## Annotation and data availability

The manual files manualYYYY.csv are reference annotations of valid trace intervals. Each row contains two integer columns, start and end, without a header. Indices are zero-based and both endpoints are inclusive. These are interval-level annotations, not pixel-level two-dimensional image masks, and are sufficient to reproduce the IOU, precision, recall, F1, accuracy, and segment-matching metrics.

The corresponding autoYYYY.csv files contain the proposed-method results. The exact raw source filenames and download instructions are provided above. This arrangement avoids redistributing the mission data while preserving reproducible evaluation inputs.

## Baseline reference

The baseline mentioned in the paper is based on:

https://github.com/Giacomo-Roncoroni/LPR_CE4

Baseline comparison data and scripts are not included here.

## Citation

Machine-readable citation metadata is provided in CITATION.cff. If you use this code or the evaluation annotations, cite the associated paper and the versioned GitHub release.
# Automatic Reconstruction of Sparse Lunar Penetrating Radar Data

This repository contains the cleaned open-source code for:

**Automatic Reconstruction of Sparse Lunar Penetrating Radar Data from Chang'e-4 Rover**

The reusable implementation is split into a small Python package under `src/ce4_lpr`, with two notebooks for running the reconstruction workflow and displaying the evaluation results.

## Data Sources and Scope

All Chang'e-4 LPR data used in this study are from China's Lunar and Planetary Data Release System:

<http://moon.bao.ac.cn/>

This repository does not redistribute the fully preprocessed Chang'e-4 dataset. Users can download Chang'e-4 high-frequency LPR `.2B` files from the official data portal, place them in `data_raw/`, and process them with this algorithm to obtain valid-segment reconstruction results.

The test data used in the paper correspond to the following Chang'e-4 LPR source files:

- `CE4_GRAS_LPR-2B_SCI_N_20221118015001_20221119050500_0267_A.2B`
- `CE4_GRAS_LPR-2B_SCI_N_20221119073501_20221119112000_0268_A.2B`
- `CE4_GRAS_LPR-2B_SCI_N_20221127102001_20221128110000_0270_A.2B`

Please download the required Chang'e-4 LPR files from:

<http://moon.bao.ac.cn/>

The `data_iou/` folder provides the segment CSV files used for quantitative checking in this open-source package:

- `manual*.csv`: manually interpreted valid-segment intervals.
- `auto*.csv`: valid-segment intervals produced by the proposed method.

The manual interval files can also be used as index files to quickly extract valid data sections from downloaded Chang'e-4 LPR data.

## Baseline Reference

The baseline mentioned in the paper is based on the code by G. Roncoroni et al.:

[Giacomo-Roncoroni/LPR_CE4](https://github.com/Giacomo-Roncoroni/LPR_CE4)

This repository focuses on releasing the proposed method and the associated evaluation data. Baseline comparison data and scripts are not included here.

## Repository Layout

- `src/ce4_lpr/io.py`: Chang'e LPR `.2B` reader for CH-2B high-frequency and CH-1 low-frequency files.
- `src/ce4_lpr/corrupt.py`: corrupted-trace detection and stability-weighted bilateral correction.
- `src/ce4_lpr/reconstruction.py`: automatic depth truncation, Sobel-X, IsoData thresholding, and morphological segment refinement.
- `src/ce4_lpr/preprocess.py`: optional enhancement utilities for geological interpretation.
- `src/ce4_lpr/metrics.py`: IOU, precision, recall, F1, segment matching, and yearly evaluation.
- `scripts/run_reconstruction.py`: run the full reconstruction workflow on `.2B` files.
- `scripts/evaluate_iou.py`: evaluate our detected segment CSV files against manual labels.
- `scripts/enhance_profile.py`: apply the optional image-enhancement chain to a reconstructed `.npy` radargram.
- `data_raw/`: place downloaded Chang'e-4 high-frequency LPR `.2B` files here before running the reconstruction workflow.
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

To run the reconstruction workflow, first download the required Chang'e-4 high-frequency LPR `.2B` files from the official data portal and place them in `data_raw/`:

```text
data_raw/
  CE4_GRAS_LPR-2B_SCI_N_20221118015001_20221119050500_0267_A.2B
  CE4_GRAS_LPR-2B_SCI_N_20221119073501_20221119112000_0268_A.2B
  CE4_GRAS_LPR-2B_SCI_N_20221127102001_20221128110000_0270_A.2B
```

Then run:

```powershell
$env:PYTHONPATH = "src"
python scripts/run_reconstruction.py --input-dir data_raw --output-dir outputs/reconstruction
```

The reconstructed data, detected valid segments, diagnostics, and figures will be saved under:

```text
outputs/reconstruction/
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

If you use this code or the provided data in your research, please cite the original paper:

**Automatic Reconstruction of Sparse Lunar Penetrating Radar Data from Chang'e-4 Rover**
