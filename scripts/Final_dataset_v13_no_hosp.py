import pandas as pd
import numpy as np
import os

# --- STEP 1: SETUP PATHS ---
# Define the base project directory along with the raw and processed data folders.
# These paths are used throughout the script for reading inputs and saving outputs.
base_path = '/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/data/'
raw_path = os.path.join(base_path, 'raw/')
processed_path = os.path.join(base_path, 'processed/')

# Create the processed folder if it does not already exist
if not os.path.exists(processed_path):
    os.makedirs(processed_path)

# --- STEP 2: LOAD CORE DATASET (V11) ---
# Load the cleaned V11 dataset that serves as the starting point for this step
try:
    v11_path = os.path.join(processed_path, 'FINAL_DATASET_V11_CLEAN.csv')
    df_v11 = pd.read_csv(v11_path)

    # Make sure FIPS codes are stored as integers for merging later
    df_v11['fips'] = df_v11['fips'].astype(int)

    print(f"Step 1: V11 loaded. Years: {sorted(df_v11['year'].unique())}")
    print(f"         Shape: {df_v11.shape}")

except FileNotFoundError:
    print(f"Error: Could not find V11 file at {v11_path}.")

# --- STEP 3: RUCC GEOGRAPHIC CODES (2013 Baseline) ---
# Load the RUCC classification file, which identifies how rural or urban each county is
try:
    rucc_path = os.path.join(raw_path, 'ruralurbancodes2013_med.csv')
    df_rucc = pd.read_csv(rucc_path)

    # Standardize column names to lowercase for consistency
    df_rucc.columns = df_rucc.columns.str.lower()

    # Convert FIPS values to numeric and drop anything invalid
    df_rucc['fips'] = pd.to_numeric(df_rucc['fips'], errors='coerce').fillna(0).astype(int)

    # Keep only the columns needed for the merge
    df_rucc = df_rucc[['fips', 'rucc_2013']]

    print("Step 2: RUCC 2013 baseline processed.")

except FileNotFoundError:
    print(f"Error: Could not find RUCC file at {rucc_path}.")

# --- STEP 4: MASTER MERGE ---
# Merge the V11 dataset with the RUCC geographic classifications.
# This step adds rural/urban context to each county observation.
df_v13 = pd.merge(df_v11, df_rucc, on='fips', how='left')

# Create broader geographic groupings based on RUCC codes
conditions = [
    (df_v13['rucc_2013'] == 1),
    (df_v13['rucc_2013'].isin([2, 3])),
    (df_v13['rucc_2013'] >= 4)
]

# Assign readable labels for county types
df_v13['geo_type'] = np.select(conditions, ['Urban', 'Suburban', 'Rural'], default='Unknown')

# Binary indicator used later in regression models
df_v13['is_rural']  = np.where(df_v13['rucc_2013'] >= 4, 1, 0)

print(f"\nStep 3: Merge complete.")
print(f"         Shape: {df_v13.shape}")
print(f"         Years: {sorted(df_v13['year'].unique())}")

# Quick check to confirm key years are still present after the merge
for yr in [2019, 2020]:
    count = (df_v13['year'] == yr).sum()
    if count == 0:
        print(f"WARNING: Year {yr} has 0 rows.")
    else:
        print(f"OK: Year {yr} has {count} rows.")

# --- STEP 5: EXPORT ---
# Save the final dataset used for the main analysis
output_csv  = os.path.join(processed_path, 'FINAL_DATASET_V13_NO_HOSP.csv')
output_xlsx = os.path.join(processed_path, 'FINAL_DATASET_V13_NO_HOSP.xlsx')

# Primary output used by the regression scripts
df_v13.to_csv(output_csv, index=False)
print(f"\nStep 4a: CSV saved to {output_csv}")

# Also export to Excel for easier inspection if needed
try:
    df_v13.to_excel(output_xlsx, index=False, engine='openpyxl')
    print(f"Step 4b: Excel saved to {output_xlsx}")
except Exception as e:
    print(f"Excel export failed: {e}")

print("\n--- V13 NO HOSPITALIZATION COMPLETE ---")
print(f"Final shape : {df_v13.shape}")
print(f"Final years : {sorted(df_v13['year'].unique())}")
print(f"Columns     : {df_v13.columns.tolist()}")