# Seoul Air Quality Monitoring Station Placement

**IT135IU – Introduction to Data Science | Topic 2**

Research question: **In which district should Seoul add an air-quality monitoring station?**

The project combines hourly air-quality measurements from 2022 with district population and area data. The notebooks profile and clean the data, compare pollution across Seoul's 25 districts, and produce a shortlist for further monitoring-coverage assessment.

## 1. Repository files

| File | Purpose |
| --- | --- |
| `Visualization_finalllll.ipynb` | Latest analysis and visualization notebook; start here. |
| `D2_Topic02_Group_(1).ipynb` | D2 data profiling, cleaning, manipulation, and bias analysis. |
| `D2_Group2_Final.ipynb` | Earlier D2 compilation, including the team's data-source and attribution record. |
| `MergeScript.py` | Optional pipeline to rebuild the merged CSV from three original source files. |
| `seoul_air_quality_2022_english.csv` | Prepared dataset used by the notebooks; already included. |
| `requirements.txt` | Pinned Python packages for pip installation. |
| `environment.yml` | Conda environment using the same `requirements.txt`. |
| Other `Project*`, `Visualization*`, and `draft_air.ipynb` files | Earlier working versions; not prerequisites for the latest notebook. |

The latest notebook is self-contained: run its cells in order. You do not need to run the older notebooks or `MergeScript.py` first.

## 2. Set up the environment

Use **Python 3.12** and Git. Choose **one** installation method below. An internet connection is required to clone the repository and install packages; the main analysis reads the included CSV locally.

The direct dependencies are pandas and NumPy for data processing, SciPy for statistics, Matplotlib and seaborn for plots, and adjustText for chart labels. JupyterLab, ipykernel, and nbconvert provide notebook editing and execution.

### Clone the repository

```bash
git clone https://github.com/thientuwl/PROJECT_INTRO-TO-DATA-SCIENCE.git
cd PROJECT_INTRO-TO-DATA-SCIENCE
```

Keep the terminal in this repository folder for all following commands. The notebooks and merge script use paths relative to the current working directory.

### Option A: pip and a virtual environment

**Windows PowerShell:**

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, use the environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m jupyter lab
```

When using this fallback, replace `python` with `.\.venv\Scripts\python.exe` in the remaining commands.

**macOS / Linux:**

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Option B: Conda

From Anaconda Prompt or a terminal with Conda available:

```bash
conda env create -f environment.yml
conda activate seoul-air-quality
```

Run this from the repository root so Conda can find `requirements.txt`. The YAML selects Python 3.12 and installs the pinned Python packages from that file.

### Check the installation

In the activated environment:

```bash
python --version
python -m pip check
python -c "import pandas, numpy, scipy, matplotlib, seaborn, adjustText; print('All analysis imports OK')"
```

Python should report `3.12.x`, and the final command should print `All analysis imports OK`.

## 3. Run the analysis

### JupyterLab

```bash
python -m jupyter lab
```

1. Open **`Visualization_finalllll.ipynb`** in JupyterLab.
2. Use the Python kernel from the environment you just installed.
3. Select **Kernel → Restart Kernel and Run All Cells**.
4. Wait for execution to finish, then save the notebook to retain the new outputs.

Tables and figures appear inside the notebook. Expected outputs include the data profile, missing-hour checks, pollutant exceedance rates, district screening table, final shortlist, statistical comparisons, and charts of monthly PM2.5, district PM2.5, population density, and screening criteria.

The notebook does not automatically export separate result CSVs or image files.

### VS Code (alternative)

Install the Python and Jupyter extensions, open the repository folder, open the latest notebook, and select the `.venv` or `seoul-air-quality` interpreter using **Select Kernel**. Run all cells from the top.

If the environment is missing from the kernel picker, register it from the activated environment:

```bash
python -m ipykernel install --user --name seoul-air-quality --display-name "Python (seoul-air-quality)"
```

Then select **Python (seoul-air-quality)**.

### Run from the terminal

From the repository root and activated environment:

```bash
python -m jupyter nbconvert --to notebook --execute "Visualization_finalllll.ipynb" --output "Visualization.executed.ipynb" --output-dir outputs --ExecutePreprocessor.timeout=600 --ExecutePreprocessor.kernel_name=python3
```

This executes every cell in a fresh kernel and saves the result to `outputs/Visualization.executed.ipynb`. The timeout is 600 seconds **per cell**. If a cell fails, nbconvert reports the error instead of treating the run as successful.

To export the executed notebook as HTML:

```bash
python -m jupyter nbconvert --to html "outputs/Visualization.executed.ipynb" --output-dir outputs
```

For the separate D2 profiling notebook:

```bash
python -m jupyter nbconvert --to notebook --execute "D2_Topic02_Group_(1).ipynb" --output "D2.executed.ipynb" --output-dir outputs --ExecutePreprocessor.timeout=600 --ExecutePreprocessor.kernel_name=python3
```

## 4. Data and reproducibility notes

The included CSV contains **216,545 rows and 17 columns**, covering **25 districts and 25 stations**, from **2022-01-01 00:00:00** to **2022-12-31 23:00:00**.

| Columns | Meaning / original units |
| --- | --- |
| `datetime`, `station_code`, `district`, `district_code`, `year` | Observation time and station/district identifiers. |
| `CO`, `NO2`, `O3`, `SO2` | Hourly gaseous pollutant concentrations in ppm. |
| `PM10`, `PM2.5` | Hourly particulate concentrations in µg/m³. |
| `population`, `households`, `male_population`, `female_population` | District demographic counts. |
| `area_km2`, `population_density` | District area in km² and population density in people/km². |

Important settings in `Visualization_finalllll.ipynb`:

- Missing pollutant values in existing rows are filled with medians grouped by station, hour, and season. The **2,455 absent station-hours** are reported separately; no new hourly rows are inserted.
- Gas conversions create additional columns in µg/m³ using the factors recorded in the notebook. The original ppm columns remain available.
- `MIN_HOURS = 1`: a day with at least one observed hourly row is included in the daily analysis. This is the latest notebook's current setting; changing it can change exceedance rates and rankings.
- The screening rule uses the 75th percentile (`q=0.75`), at least one pollution-hazard criterion, and at least one demographic-exposure criterion. The notebook also checks `q=0.70` and `q=0.80`.
- Use the computed `final_shortlist` table when checking results. It is a district-level screening result for further assessment; the analysis does not determine an exact street address for a new station.

Use the same CSV, package versions, notebook, and settings when comparing runs. Earlier notebooks can use different rules. Some earlier versions contain `!pip install adjustText`; with this environment, adjustText is already installed, so those installation-only lines can be skipped.

### Data sources and attribution

The team's source, retrieval-date, usage-term, and attribution record is in `D2_Group2_Final.ipynb`. It identifies the Seoul Metropolitan Government / Seoul Open Data Plaza as the publisher and links these source datasets:

| Source | Link |
| --- | --- |
| Hourly air quality (OA-15526) | [Seoul air-pollution measurements](https://data.seoul.go.kr/dataList/OA-15526/A/1/datasetView.do) |
| Registered households and population | [Population statistics](https://data.seoul.go.kr/bsp/wgs/dataView/data300View/109.do) |
| Population density and district area | [Population-density statistics](https://data.seoul.go.kr/bsp/wgs/dataView/data300View/37.do) |

## 5. Optional: rebuild the merged dataset

**Skip this section to run the analysis with the included CSV.** The original three input files are not included in this repository. Obtain the matching 2022 source exports used by the team and place them beside `MergeScript.py`, with these exact filenames and headers:

| Required input file | Headers used by `MergeScript.py` |
| --- | --- |
| `AIR_HOUR_2022.csv` | `측정일시`, `측정소 코드`, `측정항목`, `평균값`, `측정기 상태` |
| `주민등록 세대 및 인구 (성별_연도별_구별) 통계.csv` | `통계연도`, `구명`, `세대수`, `인구수`, `남자인구수`, `여자인구수`, `행정동코드` |
| `인구밀도 (구별) 통계.csv` | `통계연도`, `구명`, `인구수`, `면적`, `인구밀도`, `행정동코드` |

The script reads UTF-8 CSVs with optional BOM (`utf-8-sig`). Air timestamps must match `%Y%m%d%H`, for example `2022010100`. Exports with different headers or layouts require adapting the input or the script first.

Back up the prepared CSV before rebuilding because the script overwrites it:

```bash
python -c "from shutil import copy2; copy2('seoul_air_quality_2022_english.csv', 'seoul_air_quality_2022_english.backup.csv')"
python MergeScript.py
```

The pipeline keeps measurements with instrument status `0`, maps pollutant codes, pivots to one row per station-hour, joins the 2022 demographics, translates district names, validates the joins, and writes `seoul_air_quality_2022_english.csv`.

For the team's original inputs, the expected output is 216,545 rows, 17 columns, 25 districts, and no duplicate `(datetime, station_code)` pairs. Different source exports may produce different results.

## 6. Troubleshooting

| Problem | Fix |
| --- | --- |
| `FileNotFoundError` for the prepared CSV | Start Jupyter or nbconvert from the repository root and keep the included CSV beside the notebooks. |
| `FileNotFoundError` when running `MergeScript.py` | Supply all three original source files with the exact filenames above, or use the already merged CSV. |
| `ModuleNotFoundError`, including `adjustText` | Activate the environment, run `python -m pip install -r requirements.txt`, and select that environment's kernel. |
| PowerShell refuses `Activate.ps1` | Use the `.venv\Scripts\python.exe` commands above. |
| `NameError` for variables such as `df_prof` or `rule_df` | Restart the kernel and run all cells in order. |
| `KeyError` for a column | Check that you are using the included CSV; for raw rebuilding, check the source headers above. |
| `No such kernel` | Start Jupyter from the installed environment, or register it with the ipykernel command above. |
| Different rankings or figures | Confirm the notebook filename, CSV, package versions, `MIN_HOURS`, and screening thresholds match. |
