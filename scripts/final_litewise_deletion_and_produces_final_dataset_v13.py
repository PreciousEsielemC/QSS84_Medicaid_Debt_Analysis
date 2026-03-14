import pandas as pd
import numpy as np
import os
import re

# --- STEP 1: SETUP PATHS ---
# Define the project directory structure.
# This organizes the workflow into raw data inputs and processed outputs.
base_path = '/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/data/'
raw_path = os.path.join(base_path, 'raw/')
processed_path = os.path.join(base_path, 'processed/')

# Ensure the processed data folder exists.
# If it does not exist, create it so output files can be saved safely.
if not os.path.exists(processed_path):
    os.makedirs(processed_path)

# --- STEP 2: LOAD CORE DATASET (V11) ---
# Load the cleaned Version 11 dataset containing the core county-year variables
# used in the Medicaid medical debt analysis.
try:
    v11_path = os.path.join(processed_path, 'FINAL_DATASET_V11_CLEAN.csv')
    df_v11 = pd.read_csv(v11_path)

    # Convert the FIPS county identifier to an integer to guarantee
    # consistent matching with other datasets during merges.
    df_v11['fips'] = df_v11['fips'].astype(int)

    # Print diagnostic information confirming successful loading
    print(f"Step 1: Version 11 loaded. Years in debt data: {sorted(df_v11['year'].unique())}")

except FileNotFoundError:
    print(f"Error: Could not find V11 file at {v11_path}. Check your folder.")

# --- STEP 3: RUCC GEOGRAPHIC CODES (2013 Baseline) ---
# Load Rural-Urban Continuum Codes (RUCC) which classify counties
# by their degree of urbanization and proximity to metropolitan areas.
# These codes will be used to categorize counties as Urban, Suburban, or Rural.
try:
    rucc_path = os.path.join(raw_path, 'ruralurbancodes2013_med.csv')
    df_rucc = pd.read_csv(rucc_path)

    # Standardize column names to lowercase to avoid merge errors
    df_rucc.columns = df_rucc.columns.str.lower()

    # Convert FIPS identifiers to integers for compatibility with the main dataset
    df_rucc['fips'] = pd.to_numeric(df_rucc['fips'], errors='coerce').fillna(0).astype(int)

    # Keep only the variables required for geographic classification
    df_rucc = df_rucc[['fips', 'rucc_2013']]

    print("Step 2: RUCC 2013 baseline processed.")

except FileNotFoundError:
    print(f"Error: Could not find RUCC file at {rucc_path}.")

# --- STEP 4: CHR TRENDS (Mechanism Variable) ---
# Load County Health Rankings (CHR) trend data to obtain the measure
# "Preventable hospital stays," which is used as the mechanism variable
# for evaluating clinical impacts of Medicaid expansion.
try:
    chr_path = os.path.join(raw_path, 'chr_trends_csv_2023.csv')
    df_chr = pd.read_csv(chr_path, low_memory=False)

    # Identify rows corresponding to the "Preventable hospital stays" measure.
    # Case-insensitive matching ensures flexibility across dataset versions.
    mask = df_chr['measurename'].str.contains('Preventable hospital stays', case=False, na=False)
    df_hosp = df_chr[mask].copy()

    # Construct county FIPS codes using state and county numeric codes.
    df_hosp['fips'] = ((df_hosp['statecode'] * 1000) + df_hosp['countycode']).astype(int)

    # Extract the correct year from the CHR "yearspan" field.
    # The dataset labels observations as ranges (e.g., "2018-2019").
    # The regex below extracts the LAST year in the range.
    #
    # Example:
    # "2018-2019" → 2019 (correct alignment with other datasets)
    #
    # This correction resolves the earlier issue where rows appeared to
    # disappear after 2018 due to mismatched year labeling during merges.
    df_hosp['year'] = (
        df_hosp['yearspan']
        .astype(str)
        .str.extract(r'(\d{4})$')   # Extract final four-digit year
        .astype(float)
    )

    # Clean the hospitalization rate values.
    # Remove commas and convert the variable to numeric format.
    df_hosp['preventable_hosp_rate'] = (
        df_hosp['rawvalue']
        .astype(str)
        .str.replace(',', '', regex=False)
        .pipe(pd.to_numeric, errors='coerce')
    )

    # Retain only the variables needed for the merge
    df_hosp = df_hosp[['fips', 'year', 'preventable_hosp_rate']]

    # Print diagnostics to confirm the years available after cleaning
    print(f"Step 3: Hospitalization data fixed. Years found: {sorted(df_hosp['year'].dropna().unique())}")
    print(f"         Max year: {df_hosp['year'].max()}")

except FileNotFoundError:
    print(f"Error: Could not find CHR Trends file at {chr_path}.")

# --- STEP 5: MASTER MERGE ---
# Merge the geographic classification data into the main dataset
# using county FIPS identifiers.
df_v13 = pd.merge(df_v11, df_rucc, on='fips', how='left')

# Merge the hospitalization mechanism variable using both county and year
df_v13 = pd.merge(df_v13, df_hosp, on=['fips', 'year'], how='left')

# Create geographic categories based on RUCC classification.
# These categories simplify the interpretation of rural-urban differences.
conditions = [
    (df_v13['rucc_2013'] == 1),
    (df_v13['rucc_2013'].isin([2, 3])),
    (df_v13['rucc_2013'] >= 4)
]

df_v13['geo_type'] = np.select(conditions, ['Urban', 'Suburban', 'Rural'], default='Unknown')

# Binary indicator variable identifying rural counties
df_v13['is_rural'] = np.where(df_v13['rucc_2013'] >= 4, 1, 0)

# --- STEP 6: DATA AUDIT & CLEANING ---
# For the mechanism analysis, retain only observations that contain
# valid hospitalization rate values.
df_v13 = df_v13.dropna(subset=['preventable_hosp_rate'])

print(f"Step 4: Merge complete. {len(df_v13)} rows remaining.")
print(f"         Years in final dataset: {sorted(df_v13['year'].unique())}")

# Sanity checks: verify that important post-expansion years remain present
for yr in [2019, 2020]:
    count = (df_v13['year'] == yr).sum()
    if count == 0:
        print(f"WARNING: Year {yr} has 0 rows — regex fix may not have taken effect.")
    else:
        print(f"OK: Year {yr} has {count} rows.")

# --- STEP 7: EXPORT TO PROCESSED FOLDER ---
# Save the final Version 13 master dataset in both CSV and Excel formats
# for analysis and documentation.
output_csv  = os.path.join(processed_path, 'FINAL_DATASET_V13_MASTER.csv')
output_xlsx = os.path.join(processed_path, 'FINAL_DATASET_V13_MASTER.xlsx')

# Save CSV version
df_v13.to_csv(output_csv, index=False)
print(f"\nStep 5a: CSV saved to {output_csv}")

# Save Excel version
try:
    df_v13.to_excel(output_xlsx, index=False, engine='openpyxl')
    print(f"Step 5b: Excel saved to {output_xlsx}")
except Exception as e:
    print(f"Excel export failed: {e}. (Run 'pip install openpyxl' in terminal).")

# Final diagnostic summary
print("\n--- VERSION 13 MASTER COMPLETE ---")
print(f"Final dataset shape : {df_v13.shape}")
print(f"Final dataset years : {sorted(df_v13['year'].unique())}")