# PanR: Panresistome Analysis Tool

## Overview
PanR is a Python-based tool for analyzing panresistome data. It processes NCBI and Abricate summary files, merges the data, and generates visualizations such as lollipop plots, bar plots, and heatmaps. The tool is designed to help researchers analyze and visualize gene presence and prevalence across different geographic locations. It requires `ncbi_clean.csv` from [FetchM](https://github.com/Tasnimul-Arabi-Anik/FetchM) and summary files in `.tab` (preferred) or `.csv` format from [Abricate](https://github.com/tseemann/abricate). 

### Key Features:
- Merges and processes NCBI and Abricate data.
- Analyzes gene presence across samples.
- Generates visualizations for resistance gene distributions/prevalence.

## Installation

### Using `pip`
```bash
pip install panR
```

### Using `conda`
```bash
conda create -n panr_env python=3.8
conda activate panr_env
pip install git+https://github.com/Tasnimul-Arabi-Anik/PanR.git
```

### From GitHub (Manual Installation)
```bash
git clone https://github.com/Tasnimul-Arabi-Anik/PanR.git
cd PanR
pip install -r requirements.txt
```

## Usage

### Command-Line Arguments
```bash
panR --ncbi_dir <NCBI_DIRECTORY> --abricate-dir <ABRICATE_DIRECTORY> --output-dir <OUTPUT_DIRECTORY> --fig-format <FIGURE_FORMAT>
```

### Arguments
| Argument         | Description                                                |
|-----------------|------------------------------------------------------------|
| `--ncbi-dir`        | Path to `ncbi_clean.csv` file.                            |
| `--abricate-dir`| Directory containing Abricate summary `.tab` or `.csv` files. |
| `--output-dir`  | Directory to store merged results and visualizations.      |
| `--format`  | Output format for figures (`png`, `pdf`, `tiff`,`svg`).          |

### Example Run
```bash
panR --ncbi-dir ./data/ncbi_clean.csv --abricate-dir ./data/abricate --output-dir ./output --format png
```

## Outputs

- **Processed Data:** Saved in `output/` directory as `.csv`.
- **Visualizations:**
  - Heatmap of resistance genes across samples.
  ![figure1](figures/figure1.png)
  - Bar plot showing gene presence.
  ![figure3](figures/figure3.png)
  - lolipoplot showing gene counts
  ![figure2](figures/figure2.png)

## License
This tool is provided under the MIT License.

## Author
Tasnimul Arabi Anik

