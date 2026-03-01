import pandas as pd
import glob
import os

# 1. SET THE CORRECT DIRECTORY
# This ensures PyCharm looks in your 'Data for QSS_84' folder
script_dir = "/Users/preciousesielem/PycharmProjects/pythonProject4/Data for QSS_84/"
os.chdir(script_dir)

# 2. AUTOMATICALLY FIND THE V10 FILE
# This looks for any CSV file that has "V10" in the name so you don't have to type it
v10_files = glob.glob('*V10*.csv')

if not v10_files:
    print(f"ERROR: Could not find any file with 'V10' in the folder: {script_dir}")
    exit()

input_file = v10_files[0]
print(f"Found file: {input_file}")

# 3. LOAD AND FILTER
df = pd.read_csv(input_file, low_memory=False)

# Start from 2012 only (Insurance data begins in 2012)
df = df[df['year'] >= 2012].copy()

# 4. REMOVE ALL INCOMPLETE ROWS
# We delete rows missing ANY of these critical columns to ensure a balanced regression
critical_cols = [
    'share_debt_all', 'median_income', 'unemployment_rate',
    'median_age', 'pct_65_plus', 'pct_white_non_hisp', 'uninsured_rate'
]

# This drops any row where data is missing in the list above
df_clean = df.dropna(subset=critical_cols)

# 5. RE-CALCULATE PCT_POC
df_clean['pct_poc'] = 100 - df_clean['pct_white_non_hisp']

# 6. EXPORT - THIS CREATES BOTH THE CSV AND EXCEL FILES
output_csv = 'FINAL_DATASET_V11_CLEAN.csv'
output_xlsx = 'FINAL_DATASET_V11_CLEAN.xlsx'

# Save to CSV
df_clean.to_csv(output_csv, index=False)

# Save to Excel (requires 'pip install openpyxl' in your terminal)
df_clean.to_excel(output_xlsx, index=False, engine='openpyxl')

print("\n--- DATA CLEANING SUCCESSFUL ---")
print(f"Final Count: {len(df_clean)} rows")
print(f"Timeframe: {df_clean['year'].min()} to {df_clean['year'].max()}")
print(f"Created CSV: {output_csv}")
print(f"Created Excel: {output_xlsx}")