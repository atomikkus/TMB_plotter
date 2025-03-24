import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import argparse

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
    fig.savefig(f'itmb_{cancer}_{sample_name}.png', dpi=300, format='png', bbox_inches='tight', pad_inches=0.2)


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Plot TMB Distribution")
    parser.add_argument('--file', type=str, required=True, help="Path to the TSV file containing the data")
    parser.add_argument('--score', type=float, required=True, help="Patient's TMB score to highlight")
    parser.add_argument('--cancer', type=str, required=True, help="Type of cancer to filter the data")
    parser.add_argument('--sample', type=str, required=True, help="Name of the sample")

    args = parser.parse_args()



    # Call the plot function
    plot_tmb_distribution(args.file, args.score, args.cancer, args.sample)