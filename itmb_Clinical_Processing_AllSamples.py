# -*- coding: utf-8 -*-
"""
Created on Fri Sep 13 12:43:52 2024

Main script TMB_Plotter (Satya Prakash K)
Below Script is to run for All Samples (Vyomesh J)
"""

import pandas as pd
import os
import sys

# Get the input file from the first argument
if len(sys.argv) < 2:
    print("Please provide the input file as the first argument.")
    sys.exit(1)

input_file = sys.argv[1]

# Check the file extension and read accordingly
file_extension = os.path.splitext(input_file)[-1].lower()

# Read the input file based on its extension
if file_extension == '.xlsx':
    df = pd.read_excel(input_file)
elif file_extension == '.csv':
    df = pd.read_csv(input_file)
else:
    print("Unsupported file format. Please provide a .csv or .xlsx file.")
    sys.exit(1)

# Iterate over each row of the DataFrame
for index, row in df.iterrows():
    batch = row['Batch']
    sample_name = row['Sample_Name']
    cancer_type = row['Broad_Category_Cancer_Type']
    tmb_score = row['TMB_Score']
    
    # Check if TMB_Score is not missing or 'NA'
    if pd.isna(tmb_score):
        print(f"Skipping row {index + 1} due to missing TMB_Score.")
        continue

    # Combine Batch and Sample_Name into a single string
    sample_combined = f"{sample_name}_{batch}"
                
    # Prepare the command string to call script_2.py with the arguments
    command = f"python itmb_plotter2.py --file ./itmb_final.tsv --score {tmb_score} --cancer \"{cancer_type}\" --sample {sample_combined}"
    
    # Execute the command using os.system
    exit_code = os.system(command)
    
    # Check the exit code and print appropriate messages
    if exit_code == 0:
        print(f"Successfully processed row {index + 1}: Sample {sample_combined}")
    else:
        print(f"Error processing row {index + 1}. Exit code: {exit_code}")
