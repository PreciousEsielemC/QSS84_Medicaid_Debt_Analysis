import pandas as pd
import numpy as np

# --- STEP 1: LOAD YOUR CORE DATASET ---
# This is your existing cleaned file with Debt, Income, and Expansion status
try:
    df_v11 = pd.read_csv('FINAL_DATASET_V11_CLEAN.csv')
    # Ensure FIPS is an integer for perfect matching
    df_v11['fips'] = df_v11['fips'].astype(int)
    print("Step 1: Version 11 dataset loaded.")
except FileNotFoundError:
    print("Error: Could not find 'FINAL_DATASET_V11_CLEAN.csv'. Check your folder.")

# --- STEP 2: PROCESS THE 2013 RURAL-URBAN (RUCC) CODES ---
# We use 2013 as a fixed baseline to avoid "Post-Treatment Bias"
df_rucc = pd.read_csv('ruralurbancodes2013_med.csv')

# Standardize column names and force FIPS to integer
df_rucc.columns = df_rucc.columns.str.lower()
df_rucc['fips'] = pd.to_numeric(df_rucc['fips'], errors='coerce').fillna(0).astype(int)

# Keep only the code and the FIPS
df_rucc = df_rucc[['fips', 'rucc_2013']]
print("Step 2: RUCC geographic codes processed.")

# --- STEP 3: PROCESS THE HOSPITALIZATION DATA (CHR TRENDS) ---
# 'low_memory=False' prevents the DtypeWarning you saw earlier
df_chr = pd.read_csv('chr_trends_csv_2023.csv', low_memory=False)

# Filter for our 'Mechanism' variable: Preventable Hospital Stays
df_hosp = df_chr[df_chr['measurename'] == 'Preventable hospital stays'].copy()

# Create 5-digit FIPS (State + County)
df_hosp['fips'] = (df_hosp['statecode'] * 1000) + df_hosp['countycode']
df_hosp['fips'] = df_hosp['fips'].astype(int)

# Convert yearspan (e.g., 2014) to a number
df_hosp['year'] = pd.to_numeric(df_hosp['yearspan'], errors='coerce')

# CLEANING THE DATA: Remove commas from "4,583" so we can do math
df_hosp['preventable_hosp_rate'] = (
    df_hosp['rawvalue']
    .astype(str)
    .str.replace(',', '', regex=False)
    .pipe(pd.to_numeric, errors='coerce')
)

# Keep only what we need for the merge
df_hosp = df_hosp[['fips', 'year', 'preventable_hosp_rate']]
print("Step 3: Hospitalization 'mechanism' data cleaned.")

# --- STEP 4: MERGE EVERYTHING TOGETHER ---
# Join Geography
df_v12 = pd.merge(df_v11, df_rucc, on='fips', how='left')

# Join Health Rates (matching by county AND year)
df_v12 = pd.merge(df_v12, df_hosp, on=['fips', 'year'], how='left')
print("Step 4: All datasets merged successfully.")

# --- STEP 5: CREATE THE GEOGRAPHIC CATEGORIES ---
# Based on USDA Documentation:
# 1 = Urban Core
# 2-3 = Suburban/Small Metro
# 4-9 = Rural
conditions = [
    (df_v12['rucc_2013'] == 1),
    (df_v12['rucc_2013'].isin([2, 3])),
    (df_v12['rucc_2013'] >= 4)
]
choices = ['Urban', 'Suburban', 'Rural']

df_v12['geo_type'] = np.select(conditions, choices, default='Unknown')

# Create a simple 0/1 Rural dummy for interaction terms
df_v12['is_rural'] = np.where(df_v12['rucc_2013'] >= 4, 1, 0)
print("Step 5: Geographic categories created.")

# --- STEP 5: CREATE THE GEOGRAPHIC CATEGORIES ---
# [Keep your existing Step 5 code here...]
df_v12['is_rural'] = np.where(df_v12['rucc_2013'] >= 4, 1, 0)
print("Step 5: Geographic categories created.")

# --- NEW STEP: DATA QUALITY & MISSING VALUE CLEANING ---
# 1. Run the Diagnostic
missing_count = df_v12['preventable_hosp_rate'].isnull().sum()
total_rows = len(df_v12)
percent_missing = (missing_count / total_rows) * 100

print(f"\n--- Data Quality Check: Preventable Hospitalization Rate ---")
print(f"Total missing rows: {missing_count}")
print(f"Percentage of data missing: {percent_missing:.2f}%")

# 2. Check if missing data is skewed toward Rural or Urban
if missing_count > 0:
    print("\nMissing values by Geography (1=Rural, 0=Urban):")
    print(df_v12[df_v12['preventable_hosp_rate'].isnull()].groupby('is_rural').size())

# 3. Perform Listwise Deletion to ensure a Balanced Panel for QSS
# This ensures your 0.0086 result is based on complete 12-year county histories
df_v12 = df_v12.dropna(subset=['preventable_hosp_rate'])
print(f"Cleaning complete. {len(df_v12)} rows remaining for analysis.")



# --- STEP 6: SAVE THE FINAL MASTER FILES ---
df_v12.to_csv('FINAL_DATASET_V13_MASTER.csv', index=False)

# Note: requires 'pip install openpyxl'
try:
    df_v12.to_excel('FINAL_DATASET_V13_MASTER.xlsx', index=False)
    print("Step 6: Success! V12 MASTER created in CSV and Excel formats.")
except ImportError:
    print("Step 6: CSV created. (Install openpyxl for Excel export).")

print("\n--- FINAL VERIFICATION ---")
print(f"Total Rows: {len(df_v12)}")
print(f"Columns: {list(df_v12.columns)}")
