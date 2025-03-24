# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 13:38:31 2024

@author: Vyomesh J
"""
import pandas as pd

# Define the path to your Excel file
excel_file_path = 'TMB_to_iTMB_Percentile.xlsx'  # Replace with the actual path to your Excel file

# Load the two subsheets from the Excel file into DataFrames
df1 = pd.read_excel(excel_file_path, sheet_name='Sheet1')  # Replace 'SubSheet1' with the actual name of the first sheet
df2 = pd.read_excel(excel_file_path, sheet_name='Sheet2')  # Replace 'SubSheet2' with the actual name of the second sheet

# Display the first few rows of each DataFrame to verify successful loading
print("DataFrame 1 (SubSheet 1):")
print(df1.head())

print("\nDataFrame 2 (SubSheet 2):")
print(df2.head())

# Define percentiles columns for reference
percentiles_columns = [
    "5th", "10th", "15th", "20th", "25th", "30th", "35th", "40th", "45th", "50th",
    "55th", "60th", "65th", "70th", "75th", "80th", "85th", "90th", "95th", "100th"
]

# Function to determine TMB_Percentile
def get_percentile(cancer_type, tmb_score, percentiles_df):
    cancer_row = percentiles_df[percentiles_df["Cancer"] == cancer_type]
    if cancer_row.empty:
        return None  # Return None if cancer type not found
    
    for col in percentiles_columns:
        if tmb_score <= cancer_row[col].values[0]:
            return int(col.replace("th", ""))  # Return the percentile as integer
    return 100  # If score is higher than 100th percentile

# Apply the function to add TMB_Percentile column
df1["TMB_Percentile"] = df1.apply(
    lambda row: get_percentile(row["Broad_Category_Cancer_Type"], row["TMB_Score"], df2), axis=1
)

# Save the updated DataFrame to a new Excel file
output_file_path = 'TMB_Percentile_Output_V2_b261_b272.xlsx'  # Replace with your desired output path
df1.to_excel(output_file_path, index=False)

# Display the path of the output file
print(f"\nOutput saved to {output_file_path}")
