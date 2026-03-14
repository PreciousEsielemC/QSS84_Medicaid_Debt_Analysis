import pandas as pd
import glob
import os
import re

# Define project directory structure.
# These paths organize where raw input files are stored and where cleaned
# datasets will be exported for analysis.
base_path = '/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/data/'
raw_path = os.path.join(base_path, 'raw/')
processed_path = os.path.join(base_path, 'processed/')

# ============================================================
# DATA VALIDATION TEST
# This script processes all ACS 5-Year DP03 economic profile files
# and extracts the county-level unemployment rate variable.
#
# The goal is to confirm that the economic cleaning pipeline
# correctly identifies the unemployment column across all years
# and produces consistent county-year observations.
# ============================================================

# Search the raw data directory recursively for ACS DP03 data files.
# The pattern identifies files containing "DP03" and "Data.csv".
search_pattern = os.path.join(raw_path, '**/*DP03*Data.csv')

# Restrict the file list to ACS 5-Year datasets only.
# These datasets are preferred because they provide stable estimates
# for smaller counties.
files_5Y = [f for f in glob.glob(search_pattern, recursive=True) if '5Y' in f]

print(f"Found {len(files_5Y)} 5Y DP03 files\n")

# Container for storing cleaned county-year results from each file
all_results = []

# Process each DP03 file individually
for path in sorted(files_5Y):

    # Extract the filename to identify the year
    fname = os.path.basename(path)

    # Use regex to detect the four-digit year embedded in the filename
    year_match = re.search(r'20\d{2}', fname)

    # Skip files where a year cannot be identified
    if not year_match:
        print(f"SKIP (no year): {fname}")
        continue

    # Convert the detected year string to an integer
    year = int(year_match.group())

    # Load the dataset
    df = pd.read_csv(path, low_memory=False)

    # Extract column labels from the first row.
    # ACS files often contain descriptive labels in the first row
    # rather than standard column headers.
    labels = df.iloc[0].fillna('').astype(str).str.lower().str.replace(':', '').str.strip()

    # Remove the label row so only numeric data remains
    df = df.drop(0).reset_index(drop=True)

    # --- ECONOMIC VARIABLE EXTRACTION ---
    # The unemployment rate is stored in column DP03_0009PE,
    # which represents the percent of the labor force unemployed.
    # If this column does not exist, the file cannot be used.
    if 'DP03_0009PE' not in df.columns:
        print(f"{year}: ERROR — DP03_0009PE not in columns!")
        continue

    # Convert unemployment rate values to numeric format
    df['unemployment_rate'] = pd.to_numeric(df['DP03_0009PE'], errors='coerce')

    # Extract the county FIPS code from the GEO_ID column
    df['fips'] = df['GEO_ID'].str[-5:]

    # Assign the dataset year to all observations in the file
    df['year'] = year

    # Retain only the variables required for the economic dataset
    result = df[['fips', 'year', 'unemployment_rate']].copy()

    # Compute diagnostics for data quality checks
    null_count = result['unemployment_rate'].isna().sum()
    sample = result['unemployment_rate'].dropna().head(3).tolist()

    # Print summary information for the current year
    print(f"{year}: {len(result)} rows | {null_count} nulls | sample={sample}")

    # Append the cleaned data to the results list
    all_results.append(result)

# ------------------------------------------------------------
# COMBINE ALL YEARLY DATASETS
# After processing each individual DP03 file, concatenate the
# results into a single county-year dataset.
# ------------------------------------------------------------
print("\n--- COMBINING ALL YEARS ---")

combined = pd.concat(all_results, ignore_index=True)

print(f"Total rows: {len(combined)}")
print(f"Years: {sorted(combined['year'].unique())}")

# Evaluate missing data patterns by year
# This helps verify whether any ACS releases contain abnormal
# levels of missing unemployment values.
print("\nNull % by year:")
print(combined.groupby('year')['unemployment_rate']
      .apply(lambda x: f"{x.isna().mean()*100:.1f}% null").to_string())

# ------------------------------------------------------------
# EXPORT CLEANED DATASET
# Save the final combined unemployment dataset to the processed
# data directory for use in the master analysis dataset.
# ------------------------------------------------------------
out = os.path.join(processed_path, 'cleaned_econ_v10.csv')

combined.to_csv(out, index=False)

print(f"\nSaved to: {out}")