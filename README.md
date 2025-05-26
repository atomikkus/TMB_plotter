# iTMB plotting of Cancer Types and Samples

i-TMB plot is a density plot, the height of the plot at a specific point represents the probability density at that point. A higher density value indicates a higher concentration of data points around that particular value, while a lower density value suggests fewer data points in that region. The interpretation can be simplified as follows: When a patient's TMB score is 15 with a density of 0.02, it suggests that there are 2% of patients with a TMB score of approximately 15 in the dataset.

![image](https://github.com/atomikkus/TMB_plotter/assets/87168509/43a9be7a-2315-46a7-8be8-e152763aa91a)



#### ** The clinical outcomes of patients with cancer can vary significantly across different geographies, highlighting the complexity of utilizing TMB as a predictive immunotherapy biomarker.
#### ** It is important to recognize that assuming a universal criterion and cutoff for all ethnicities and geographical areas may have adverse effects on cancer patients. Therefore, caution should be exercised when interpreting TMB data, considering the diverse factors that influence its efficacy as a biomarker in clinical settings.

---

## Requirements

The following versions are used in the current virtual environment for full reproducibility:

- numpy==2.2.6
- pandas==2.2.3
- matplotlib==3.10.3
- scipy==1.15.3
- tqdm==4.67.1

Install dependencies with:

```bash
pip install -r requirements.txt
```

---

## Usage

### Single Sample Plotting

Generate a TMB percentile plot for a single patient:

```bash
python itmb_plotter2.py --file itmb_final.tsv --score 5.2 --cancer Lung --sample SAMPLE123
```
- `--file`: Path to the base TMB distribution data (TSV, must have 'Broad Category Cancer Type' and 'TMB Score' columns)
- `--score`: Patient's TMB score
- `--cancer`: Cancer type (must match a value in the base data)
- `--sample`: Sample name (used for output file naming)

### Batch Processing

Process a batch of patients from a TSV file (columns: `ID`, `Broad-Type`, `TMB`).

#### Only Percentiles (no plots):
```bash
python itmb_plotter2.py --file itmb_final.tsv --batch BATCH.tsv --only-percentiles
```
- Outputs a new TSV file `batch_results_with_percentiles.tsv` with an added `Percentile` column for each patient.

#### All (percentiles + plots):
```bash
python itmb_plotter2.py --file itmb_final.tsv --batch BATCH.tsv --all
```
- Outputs `batch_results_with_percentiles.tsv` as above.
- Generates a plot for each patient in the batch.
- All generated plots are automatically zipped into `itmb_plots_archive.zip` and the individual PNG files are deleted to save space.

#### Example Batch File Format
```
ID	Broad-Type	TMB
IN-423-VJ5G	Breast	4.77
IN-423-VJCD	Head and Neck	5
IN-423-VJCJ	Breast	5.23
```

---

## Notes
- The script uses IQR-based outlier removal for percentile calculation and plotting.
- Progress bars are shown for batch processing and zipping using `tqdm`.
- If you process a large batch, all plots are zipped and originals are deleted to save disk space.
- For any issues, check the terminal output for warnings or errors.

