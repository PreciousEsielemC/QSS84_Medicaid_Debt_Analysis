import pandas as pd
import glob
import os
import re
import numpy as np

# -------------------------------------------------------------
# DATA PIPELINE SCRIPT: BUILD MASTER ANALYSIS DATASET
# -------------------------------------------------------------
# This script performs the full data preparation pipeline for
# the Medicaid Expansion and Medical Debt project.
#
# The workflow includes:
#   1. Cleaning raw ACS tables (income, demographics, insurance)
#   2. Standardizing county identifiers and years
#   3. Reshaping medical debt data into panel format
#   4. Merging all sources into a single county-year dataset
#   5. Creating key analysis variables
#   6. Exporting the final master dataset for econometric analysis
#
# Final output: a panel dataset where
#   Unit of observation = County-Year
# -------------------------------------------------------------


# -------------------------------------------------------------
# STEP 1: DEFINE FILE PATHS AND DIRECTORY STRUCTURE
# -------------------------------------------------------------
# Establish absolute paths to the project's raw data and
# processed data directories.

base_path = '/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/data/'
raw_path = os.path.join(base_path, 'raw/')
processed_path = os.path.join(base_path, 'processed/')

# Create the processed folder if it does not already exist
if not os.path.exists(processed_path):
    os.makedirs(processed_path)

# Change working directory to the raw data folder so file
# searches operate relative to the source data location.
os.chdir(raw_path)

# Version tag for output files to track dataset revisions
VERSION = 'v10'


# -------------------------------------------------------------
# STEP 2: GENERALIZED DATA CLEANER FUNCTION
# -------------------------------------------------------------
# This function extracts relevant variables from different
# American Community Survey (ACS) tables.
#
# It identifies variables based on column labels rather than
# fixed column names, making the cleaning process robust to
# minor structural changes across ACS files and years.

def bulletproof_cleaner_v15(file_path, table_type):

    try:
        # Load the raw ACS table
        df = pd.read_csv(file_path, low_memory=False)

        # Extract the year from the filename
        fname = os.path.basename(file_path)
        year_match = re.search(r'20\d{2}', fname)

        # Skip files without a recognizable year
        if not year_match:
            return None

        year = int(year_match.group())

        # The first row of ACS files contains descriptive labels
        # rather than numeric values; extract these labels to
        # identify target variables.
        labels = df.iloc[0].fillna('').astype(str).str.lower().str.replace(':', '').str.strip()

        # Remove the label row to retain only data rows
        df = df.drop(0)

        # Dictionaries and lists used to store identified columns
        target_cols = {}
        no_ins_cols = []
        total_pop_col = None


        # -----------------------------------------------------
        # IDENTIFY RELEVANT VARIABLES BY TABLE TYPE
        # -----------------------------------------------------

        for col in df.columns:
            lbl = labels[col]

            if not lbl:
                continue

            # --- INCOME TABLE (ACS S1903) ---
            # Extract median household income estimates.
            if table_type == 'income':
                if 'median income' in lbl and 'estimate' in lbl:
                    if 'households' in lbl:
                        if 'median_income' not in target_cols:
                            target_cols['median_income'] = col

            # --- DEMOGRAPHICS TABLE (ACS DP05) ---
            # Extract demographic indicators such as race,
            # median age, and elderly population share.
            elif table_type == 'demo':

                # Percent White, Non-Hispanic
                if 'white alone' in lbl and 'not hispanic' in lbl and 'percent' in lbl:
                    if 'margin' not in lbl:
                        target_cols['pct_white_non_hisp'] = col

                # Median Age
                if 'median age' in lbl and 'margin' not in lbl:
                    if 'percent' not in lbl and 'male' not in lbl and 'female' not in lbl:
                        if 'median_age' not in target_cols:
                            target_cols['median_age'] = col

                # Population age 65+
                if '65 years' in lbl and 'percent' in lbl and 'margin' not in lbl:
                    if 'male' not in lbl and 'female' not in lbl:
                        if 'pct_65_plus' not in target_cols or col == 'DP05_0024PE':
                            target_cols['pct_65_plus'] = col


            # --- ECONOMIC VARIABLES ---
            # Economic data (including unemployment rate) are
            # already cleaned separately in cleaned_econ_v10.csv.
            # Therefore, this script skips econ extraction here.

            # --- INSURANCE TABLE (ACS B27001) ---
            # Used to calculate the share of residents without
            # health insurance coverage.
            elif table_type == 'insurance':

                # Total population count
                if lbl in ('estimate!!total', 'total estimate'):
                    total_pop_col = col

                # Population without health insurance
                if 'no health insurance coverage' in lbl and 'estimate' in lbl and 'margin' not in lbl:
                    no_ins_cols.append(col)


        # -----------------------------------------------------
        # CONSTRUCT CLEAN DATASETS
        # -----------------------------------------------------

        # --- INSURANCE RATE CALCULATION ---
        # Calculate uninsured rate as:
        # (population without insurance / total population) * 100
        if table_type == 'insurance' and total_pop_col and no_ins_cols:

            clean = df[['GEO_ID', total_pop_col] + no_ins_cols].copy()

            for c in [total_pop_col] + no_ins_cols:
                clean[c] = pd.to_numeric(clean[c], errors='coerce')

            clean['uninsured_rate'] = (clean[no_ins_cols].sum(axis=1) / clean[total_pop_col]) * 100

            clean['fips'] = clean['GEO_ID'].str[-5:]
            clean['year'] = year

            return clean[['fips', 'year', 'uninsured_rate']]


        # --- GENERAL CLEANING FOR OTHER TABLE TYPES ---
        elif target_cols:

            clean = df[['GEO_ID'] + list(target_cols.values())].copy()
            clean = clean.rename(columns={v: k for k, v in target_cols.items()})

            clean['fips'] = clean['GEO_ID'].str[-5:]
            clean['year'] = year

            for c in target_cols.keys():
                clean[c] = pd.to_numeric(clean[c], errors='coerce')

            return clean[['fips', 'year'] + list(target_cols.keys())]

    except Exception as e:
        print(f"  Error in {os.path.basename(file_path)}: {e}")

    return None


# -------------------------------------------------------------
# PHASE 1: CLEAN RAW ACS TABLES
# -------------------------------------------------------------
# This stage processes the three ACS tables required for the
# analysis:
#
#   income     → Median household income
#   demo       → Demographic characteristics
#   insurance  → Health insurance coverage rates
#
# Economic variables are handled separately and already exist
# in cleaned_econ_v10.csv.

targets = {'income': 'S1903', 'demo': 'DP05', 'insurance': 'B27001'}

for key, table_id in targets.items():

    search_pattern = os.path.join(raw_path, f"**/*{table_id}*Data.csv")

    # Only use ACS 5-Year estimates to ensure stability
    files = [f for f in glob.glob(search_pattern, recursive=True) if "5Y" in f]

    print(f"Cleaning {key} ({len(files)} files found)...")

    processed = [bulletproof_cleaner_v15(f, key) for f in files]
    valid_dfs = [d for d in processed if d is not None]

    if valid_dfs:
        combined = pd.concat(valid_dfs, ignore_index=True)

        out_path = os.path.join(processed_path, f"cleaned_{key}_{VERSION}.csv")

        combined.to_csv(out_path, index=False)

        print(f"  Saved {len(combined)} rows → years: {sorted(combined['year'].unique())}")

    else:
        print(f"  WARNING: No valid data found for {key}!")


# -------------------------------------------------------------
# PHASE 2: MASTER DATASET MERGE
# -------------------------------------------------------------
# This stage merges all cleaned datasets together into a
# unified county-year panel dataset.

print("\nStarting Master Merge...")

df_inc      = pd.read_csv(processed_path + f'cleaned_income_{VERSION}.csv',    dtype={'fips': str})
df_ec       = pd.read_csv(processed_path + f'cleaned_econ_{VERSION}.csv',      dtype={'fips': str})
df_dem      = pd.read_csv(processed_path + f'cleaned_demo_{VERSION}.csv',      dtype={'fips': str})
df_ins      = pd.read_csv(processed_path + f'cleaned_insurance_{VERSION}.csv', dtype={'fips': str})
df_debt_raw = pd.read_csv(raw_path + 'Urban_Institute_data_1.csv',             dtype={'fips': str})

# Medicaid expansion data from KFF
df_med      = pd.read_csv(raw_path + 'medicaid_expansion_kff.csv', skiprows=2)

df_med['expansion_year'] = pd.to_datetime(
    df_med['Expansion Implementation Date'],
    errors='coerce'
).dt.year


# Quick diagnostic check for unemployment data coverage
print(f"  Econ years loaded: {sorted(df_ec['year'].unique())}")
print(f"  Econ null % unemployment: "
      f"{df_ec['unemployment_rate'].isna().mean()*100:.1f}%")


# -------------------------------------------------------------
# STANDARDIZE FIPS CODES
# -------------------------------------------------------------
# Ensure all datasets use a 5-digit zero-padded FIPS code
# to prevent merge mismatches.

for d in [df_inc, df_ec, df_dem, df_ins, df_debt_raw]:
    d['fips'] = d['fips'].astype(str).str.zfill(5)


# -------------------------------------------------------------
# RESHAPE MEDICAL DEBT DATA
# -------------------------------------------------------------
# Convert the Urban Institute dataset from wide format
# (one column per year) into long format so it matches
# the panel structure used in the econometric models.

df_long = pd.melt(
    df_debt_raw[df_debt_raw['metric'] == 'share_debt_all'],
    id_vars=['fips', 'full_name'],
    value_vars=[str(y) for y in range(2011, 2024)],
    var_name='year',
    value_name='share_debt_all'
).astype({'year': int})

# Extract state name from the county identifier
df_long['state_name'] = df_long['full_name'].str.split(', ').str[-1]


# -------------------------------------------------------------
# MERGE ALL DATA SOURCES
# -------------------------------------------------------------
# Sequentially merge all cleaned datasets into the main panel.

final = (df_long
         .merge(df_inc, on=['fips', 'year'], how='left')
         .merge(df_ec,  on=['fips', 'year'], how='left')
         .merge(df_dem, on=['fips', 'year'], how='left')
         .merge(df_ins, on=['fips', 'year'], how='left')
         .merge(df_med[['Location', 'expansion_year']],
                left_on='state_name', right_on='Location', how='left'))


# -------------------------------------------------------------
# CREATE ANALYSIS VARIABLES
# -------------------------------------------------------------

# Medicaid expansion indicator
final['medicaid_expansion'] = (
    (final['expansion_year'].notna()) &
    (final['year'] >= final['expansion_year'])
).astype(int)

# Percent population of color
final['pct_poc'] = 100 - final['pct_white_non_hisp']

# Remove rows that are not valid county entries
final = final[final['full_name'].str.contains(',', na=False)]

# Remove intermediate merge variables
final = final.drop(columns=['expansion_year', 'Location', 'state_name'])


# -------------------------------------------------------------
# PHASE 3: EXPORT FINAL DATASET
# -------------------------------------------------------------
# Save the completed county-year panel dataset in both CSV
# and Excel formats for use in analysis scripts and reporting.

final.to_csv(os.path.join(processed_path, 'FINAL_PROJECT_DATASET_V10.csv'), index=False)

final.to_excel(
    os.path.join(processed_path, 'FINAL_PROJECT_DATASET_V10.xlsx'),
    index=False,
    engine='openpyxl'
)


print(f"\n--- V10 COMPLETE ---")
print(f"Shape: {final.shape}")
print(f"Years: {sorted(final['year'].unique())}")


# -------------------------------------------------------------
# DATA QUALITY CHECKS
# -------------------------------------------------------------
# Report the percentage of missing values by year for all
# critical analysis variables.

print("\n--- NULL % BY YEAR FOR CRITICAL COLUMNS ---")

critical = [
    'share_debt_all',
    'median_income',
    'unemployment_rate',
    'uninsured_rate',
    'median_age',
    'pct_65_plus',
    'pct_white_non_hisp'
]

for col in critical:

    if col in final.columns:

        by_year = final.groupby('year')[col].apply(
            lambda x: f"{x.isna().mean()*100:.0f}%"
        )

        nulls = [f"{y}:{v}" for y, v in by_year.items()]

        print(f"  {col:25s}: {' | '.join(nulls)}")