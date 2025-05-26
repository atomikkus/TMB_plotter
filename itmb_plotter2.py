import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import argparse
from scipy.stats import percentileofscore
from tqdm import tqdm
import zipfile
import os

def get_tmb_percentile(base_df_path, patient_score, cancer_type):
    """
    Calculate the percentile of a patient's TMB score for a specific cancer type
    using the same outlier removal logic as plot_tmb_distribution.
    """
    try:
        df = pd.read_csv(base_df_path, sep="\t")
    except FileNotFoundError:
        print(f"Error: Base data file {base_df_path} not found for percentile calculation.")
        return np.nan
    
    ndf = df[df['Broad Category Cancer Type'] == cancer_type].copy()

    if ndf.empty or 'TMB Score' not in ndf.columns:
        # print(f"Warning: No data found for cancer type '{cancer_type}' or 'TMB Score' column missing in {base_df_path} for percentile calculation.")
        return np.nan

    ndf_tmb_scores = ndf['TMB Score'].dropna()
    if ndf_tmb_scores.empty:
        # print(f"Warning: No valid TMB scores found for cancer type '{cancer_type}' after dropping NA for percentile calculation.")
        return np.nan

    Q1 = ndf_tmb_scores.quantile(0.25)
    Q3 = ndf_tmb_scores.quantile(0.75)
    IQR = Q3 - Q1

    if IQR == 0: # Avoid division by zero or issues if all values are the same
        # If all values are identical, use all non-NA scores for percentile calculation.
        # percentileofscore handles this appropriately.
        cdf_tmb_scores = ndf_tmb_scores
    else:
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        cdf_tmb_scores = ndf_tmb_scores[(ndf_tmb_scores >= lower_bound) & (ndf_tmb_scores <= upper_bound)]

    if cdf_tmb_scores.empty:
        # print(f"Warning: No TMB scores remaining for cancer type '{cancer_type}' after outlier removal for percentile calculation. May use original scores or return NaN.")
        # Fallback: if outlier removal results in empty set, consider if percentile against non-filtered set is desired, or return NaN.
        # For consistency with plotting which uses filtered data, an empty cdf means no reference distribution points.
        return np.nan
    
    percentile = percentileofscore(cdf_tmb_scores, patient_score, kind='rank')
    return percentile

def plot_tmb_distribution(df_path, score, cancer, sample_name):
    """
    Plot a TMB (Tumor Mutation Burden) rug plot for a specific cancer type with percentiles and patient score.

    Arguments:
    df -- DataFrame containing the cancer data with 'Broad Category Cancer Type' and 'TMB Score' columns
    score -- Patient's TMB score to highlight on the plot
    cancer -- Type of cancer to filter data for (e.g., 'Lung')
    
    Outputs:
    A rug plot saved as an image file for the given cancer type.
    """
    
    # data
    df = pd.read_csv(df_path, sep="\t")
    ndf = df[df['Broad Category Cancer Type'] == cancer].copy().reset_index()

    fig, ax = plt.subplots(1, 1, figsize=(12, 4.8)) 

    # Calculate IQR
    Q1 = ndf['TMB Score'].quantile(0.25)
    Q3 = ndf['TMB Score'].quantile(0.75)
    IQR = Q3 - Q1

    # remove outliers
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    cdf = ndf[(ndf['TMB Score'] >= lower_bound) & (ndf['TMB Score'] <= upper_bound)]
    percentiles = np.percentile(cdf['TMB Score'], [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])

    # blue dots
    ax.plot(cdf['TMB Score'], np.zeros_like(cdf['TMB Score']), 'o', color='#148bcd', markersize=18, alpha=0.09)
    for p in percentiles:
        ax.axvline(p, color='black') # percentiles

    # universal TMB cutoff line
    ax.axvline(10, color='Green', linewidth=2)
    ax.plot(10, 0, 'o', color='green', markersize=20, label='Universal TMB cut-off') # marker
    ax.text(10, 0, f'10', verticalalignment='center', horizontalalignment='center', color='white', fontweight='bold', fontsize=8)

    # patient tmb
    scr = min(score, cdf['TMB Score'].max())
    ax.axvline(scr, color='Red')
    ax.plot(scr, 0, 'o', color='red', markersize=20, label='Patient TMB')
    ax.text(scr, 0, f'{score:.1f}', verticalalignment='center', horizontalalignment='center', color='white', fontweight='bold', fontsize=8)

    # indices labels (0th, 20th, 40th, 60th, 80th, 100th)
    percentile_indices = [0, 2, 4, 6, 8, 9, 10]
    for i in percentile_indices:
        ax.text(percentiles[i], 0.065, f'{int(i * 10)}th', rotation=90, verticalalignment='bottom', horizontalalignment='center', color='black')
    ax.set_yticks([])

    # legends 
    circle_legend = Line2D([0], [0], marker='o', color='w', markerfacecolor='#148bcd', markersize=18, alpha=0.3)
    handles, labels = ax.get_legend_handles_labels()
    handles.append(circle_legend)
    labels.append(f'{cancer} Cancer TMB Distribution')
    plt.legend(handles=handles, labels=labels, bbox_to_anchor=(0.8, -0.8), loc="lower right", frameon=False, ncol=3)
    ax.set_title('iTMB (Percentiles)', fontweight="bold", pad=40)

    plt.tight_layout()
    #plt.show()

    # Save the figure as a PNG file
    fig_filename = f'itmb_{cancer}_{sample_name}.png'
    fig.savefig(fig_filename, dpi=300, format='png', bbox_inches='tight', pad_inches=0.2)
    plt.close(fig)  # Close the figure to free memory
    return fig_filename

def create_plots_zip(plot_filenames, zip_filename="itmb_plots_archive.zip"):
    """
    Creates a ZIP archive from a list of plot files and deletes the original files.
    """
    if not plot_filenames:
        print("No plots were generated to archive.")
        return

    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zf:
            for plot_file in tqdm(plot_filenames, desc="Zipping plots"):
                if os.path.exists(plot_file):
                    zf.write(plot_file, os.path.basename(plot_file))
                    os.remove(plot_file) # Delete the original file after adding to zip
                else:
                    print(f"Warning: Plot file {plot_file} not found, skipping.")
        print(f"All plots have been archived into {zip_filename} and original files deleted.")
    except Exception as e:
        print(f"Error creating ZIP archive: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot TMB Distribution or process batch TMB data.")
    
    # Common argument for base data
    parser.add_argument('--file', type=str, required=True, 
                        help="Path to the TSV file containing the base TMB distribution data.")

    # Arguments for single plot mode
    parser.add_argument('--score', type=float, 
                        help="Patient's TMB score (for single plot mode).")
    parser.add_argument('--cancer', type=str, 
                        help="Type of cancer, matching 'Broad Category Cancer Type' in the base data file (for single plot mode).")
    parser.add_argument('--sample', type=str, 
                        help="Name of the sample, used for single plot mode output file name.")

    # Arguments for batch processing mode
    parser.add_argument('--batch', type=str, 
                        help="Path to a tab-separated batch file with columns: ID, Broad-Type, TMB.")
    
    batch_mode_group = parser.add_mutually_exclusive_group()
    batch_mode_group.add_argument('--only-percentiles', action='store_true', 
                               help="In batch mode, output only the batch file with an added 'Percentile' column. No plots are generated.")
    batch_mode_group.add_argument('--all', action='store_true', 
                               help="In batch mode, generate plots for all entries and output the batch file with an added 'Percentile' column.")

    args = parser.parse_args()

    if args.batch:
        # Batch processing mode
        if not (args.only_percentiles or args.all):
            parser.error("When using --batch, you must specify either --only-percentiles or --all.")

        try:
            batch_df = pd.read_csv(args.batch, sep="\t")
        except FileNotFoundError:
            print(f"Error: Batch file {args.batch} not found.")
            exit(1) # Exit if batch file not found
        except Exception as e:
            print(f"Error reading batch file {args.batch}: {e}")
            exit(1)


        required_cols = ['ID', 'Broad-Type', 'TMB']
        if not all(col in batch_df.columns for col in required_cols):
            parser.error(f"Batch file must contain the columns: {', '.join(required_cols)}.")
            exit(1)

        results_data = []
        generated_plot_files = []
        print(f"Starting batch processing from file: {args.batch}")

        for index, row in tqdm(batch_df.iterrows(), total=batch_df.shape[0], desc="Processing patients"):
            patient_id = row['ID']
            cancer_type = row['Broad-Type'] # This is 'Broad Category Cancer Type'
            tmb_score = row['TMB']
            
            percentile = get_tmb_percentile(args.file, tmb_score, cancer_type)
            
            current_result = row.to_dict()
            current_result['Percentile'] = round(percentile, 2) if not np.isnan(percentile) else np.nan
            results_data.append(current_result)

            if args.all:
                # print(f"  Generating plot for {patient_id}...") # Removed for quieter output
                plot_filename = plot_tmb_distribution(df_path=args.file, score=tmb_score, cancer=cancer_type, sample_name=str(patient_id))
                if plot_filename:
                    generated_plot_files.append(plot_filename)
                # print(f"  Plot saved for {patient_id}.") # Removed for quieter output
        
        output_df = pd.DataFrame(results_data)
        # Ensure original column order, plus Percentile at the end
        original_cols_plus_percentile = list(batch_df.columns) + ['Percentile']
        # Handle cases where 'Percentile' might have been an original column (unlikely but safe)
        if 'Percentile' in batch_df.columns:
             final_cols = [col for col in original_cols_plus_percentile if col != 'Percentile'] + ['Percentile']
        else:
            final_cols = original_cols_plus_percentile
        
        output_df = output_df[final_cols]


        output_filename = "batch_results_with_percentiles.tsv"
        try:
            output_df.to_csv(output_filename, sep="\t", index=False, float_format='%.2f', na_rep='NaN')
            print(f"Batch processing complete. Results saved to {output_filename}")
        except Exception as e:
            print(f"Error saving results to {output_filename}: {e}")
        
        # After batch processing, if plots were generated, zip them
        if args.all and generated_plot_files:
            create_plots_zip(generated_plot_files)

    else:
        # Single plot mode (original functionality)
        if not all([args.score is not None, args.cancer, args.sample]):
            parser.error("For single plot mode (when --batch is not used), --score, --cancer, and --sample are all required.")
        
        print(f"Generating single plot for sample: {args.sample}, Cancer: {args.cancer}, Score: {args.score}")
        plot_tmb_distribution(df_path=args.file, score=args.score, cancer=args.cancer, sample_name=args.sample)
        print(f"Plot saved for sample {args.sample} as itmb_{args.cancer}_{args.sample}.png")