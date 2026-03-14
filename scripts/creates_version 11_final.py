import pandas as pd
import glob
import os

# 1. SET THE DIRECTORIES
# Define the base project path and the folder where the processed datasets live.
# Using absolute paths here so the script runs reliably in PyCharm.
base_path = '/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/data/'
processed_path = os.path.join(base_path, 'processed/')

# Move into the processed data folder where the V10 dataset should already be saved
os.chdir(processed_path)

# 2. AUTOMATICALLY FIND THE V10 FILE
# Look for any CSV file that contains "V10" in the filename.
# This avoids hard-coding the exact filename in case it changes slightly.
v10_files = glob.glob('*PROJECT_DATASET_V10*.csv')

if not v10_files:
    print(f"ERROR: Could not find any file with 'V10' in: {processed_path}")
else:
    input_file = v10_files[0]
    print(f"Found input file: {input_file}")

    # 3. LOAD THE DATA
    # Read the dataset into pandas. low_memory=False helps avoid dtype issues
    # when working with large CSV files.
    df = pd.read_csv(input_file, low_memory=False)
    print(f"Initial row count: {len(df)}")

    # 4. FILTER: START FROM 2012
    # Drop 2011 observations. The 2011 data contains an insurance coverage
    # measurement issue that creates a discontinuity in the panel.
    df = df[df['year'] >= 2012].copy()
    print(f"Rows after removing 2011: {len(df)}")

    # 5. REMOVE INCOMPLETE ROWS
    # Define the variables required for the regression analysis.
    # Any observation missing one of these will be removed.
    critical_cols = [
        'share_debt_all',     # Main outcome variable
        'median_income',      # Economic control
        'unemployment_rate',  # Labor market control
        'uninsured_rate',     # Health insurance control
        'median_age',         # Demographic control
        'pct_65_plus',        # Older population share
        'pct_white_non_hisp'  # Race composition variable
    ]

    # Drop rows where any of the required variables are missing.
    # This ensures the regression sample is consistent across models.
    df_clean = df.dropna(subset=critical_cols).copy()

    # 6. RE-CALCULATE PCT_POC
    # Create a simple "percent people of color" variable from the
    # non-Hispanic white population share.
    df_clean['pct_poc'] = 100 - df_clean['pct_white_non_hisp']

    # 7. EXPORT THE CLEANED PANEL
    # Save the cleaned dataset in both CSV and Excel formats.
    output_csv = 'FINAL_DATASET_V11_CLEAN.csv'
    output_xlsx = 'FINAL_DATASET_V11_CLEAN.xlsx'

    # Save as CSV (main format used in analysis)
    df_clean.to_csv(output_csv, index=False)

    # Save as Excel in case it’s useful for manual inspection
    # or sharing the dataset outside Python
    try:
        df_clean.to_excel(output_xlsx, index=False, engine='openpyxl')
        print(f"Successfully saved Excel: {output_xlsx}")
    except Exception as e:
        print(f"Excel export failed (try 'pip install openpyxl'): {e}")

    # 8. SUMMARY STATS
    # Print a quick summary so it's easy to verify that the cleaning step worked
    print("\n--- VERSION 11 DATA CLEANING SUCCESSFUL ---")
    print(f"Final Row Count (Balanced Panel): {len(df_clean)}")
    print(f"Timeframe: {df_clean['year'].min()} to {df_clean['year'].max()}")
    print(f"Variables preserved: {', '.join(critical_cols)}")
    print(f"Created CSV: {output_csv}")