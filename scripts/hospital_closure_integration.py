"""
hospital_closure_integration.py
================================
This script integrates a rural hospital closures dataset into the main
county-year panel dataset (Version 13) used in the Medicaid expansion
medical debt analysis.

The workflow performs four major tasks:

1. Import and clean the hospital closures database.
2. Match closure records to county FIPS codes using a crosswalk and
   fuzzy matching when necessary.
3. Construct county-level closure variables describing whether and when
   a rural hospital closure occurred.
4. Estimate additional regression models testing whether hospital
   closures explain heterogeneity in Medicaid expansion effects.

New regression specifications:

  Model E — Expansion × Rural × Ever-Closed
             Tests whether the rural "friction gap" is larger in counties
             that experienced a rural hospital closure.

  Model F — Expansion × Rural split by closure status
             Separately estimates the expansion effect for rural counties
             with and without hospital closures.

REQUIREMENTS
------------
pip install fuzzywuzzy python-Levenshtein requests openpyxl
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from linearmodels.panel import PanelOLS
import os, warnings, requests

warnings.filterwarnings('ignore')

# ---------------------------------------------------------------------
# DEFINE FILE PATHS
# ---------------------------------------------------------------------
# Central project directory and key input/output files used in the script.
BASE     = '/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/'
PANEL    = os.path.join(BASE, 'data/processed/FINAL_DATASET_V13_MASTER.csv')
CLOSURES = os.path.join(BASE, 'data/raw/Closures-Database-for-Web.xlsx')
OUT_CSV  = os.path.join(BASE, 'data/processed/FINAL_DATASET_V14_CLOSURES.csv')
OUT_PNG  = os.path.join(BASE, 'figures/hospital_closure_heterogeneity.png')

# ── STEP 1: LOAD CLOSURES DATA ───────────────────────────────────────
# Import the hospital closure database and perform initial cleaning.
# The dataset contains information on U.S. hospital closures, including
# county location, closure year, and rural classification.
print("=" * 60)
print("HOSPITAL CLOSURE INTEGRATION")
print("=" * 60)

cl = pd.read_excel(CLOSURES)

# Standardize column formatting to avoid merge errors
cl.columns = cl.columns.str.strip()
cl['County/district'] = cl['County/district'].str.strip()
cl['State']           = cl['State'].str.strip()

# Convert closure year to numeric format
cl['Closure Year']    = pd.to_numeric(cl['Closure Year'], errors='coerce')

# Restrict the dataset to closures within the relevant study horizon
cl = cl[cl['Closure Year'].between(2005, 2023)].copy()

print(f"Closures loaded: {len(cl)} total, "
      f"{cl[cl['Closure Year'].between(2012,2023)].shape[0]} in study window 2012-2023")

# Identify closures that occurred in rural hospitals using RUCA classification
cl['is_rural_hospital'] = (cl['RUCA'] >= 4).astype(int)

print(f"Rural closures (RUCA>=4) in 2012-2023: "
      f"{cl[(cl['Closure Year'].between(2012,2023)) & (cl['is_rural_hospital']==1)].shape[0]}")

# ── STEP 2: GET FIPS CROSSWALK ───────────────────────────────────────
# Load a county FIPS crosswalk to match hospital closure records
# (which use county names) to numeric county identifiers.
FIPS_URL  = 'https://raw.githubusercontent.com/kjhealy/fips-codes/master/state_and_county_fips_master.csv'
FIPS_FILE = os.path.join(BASE, 'data/raw/county_fips_crosswalk.csv')

# Download the crosswalk if it does not already exist locally
if not os.path.exists(FIPS_FILE):
    print("\nDownloading FIPS crosswalk...")
    try:
        r = requests.get(FIPS_URL, timeout=10)
        with open(FIPS_FILE, 'w') as f:
            f.write(r.text)
        print("Downloaded successfully.")
    except Exception as e:
        print(f"Download failed: {e}")
        raise

# Load the FIPS crosswalk dataset
fips_xw = pd.read_csv(FIPS_FILE)
print(f"\nFIPS crosswalk loaded: {len(fips_xw)} counties")

# Standardize column names for compatibility
if 'state_abbr' in fips_xw.columns:
    fips_xw = fips_xw.rename(columns={'state_abbr': 'state'})
if 'county_name' in fips_xw.columns:
    fips_xw = fips_xw.rename(columns={'county_name': 'name'})

# Clean county names to improve matching accuracy
fips_xw['name_clean'] = (fips_xw['name']
                          .str.strip()
                          .str.replace(r'\s+(County|Parish|Borough|Census Area|'
                                       r'Municipality|City and Borough|District)$',
                                       '', regex=True)
                          .str.strip()
                          .str.lower())

# Standardize state abbreviations
fips_xw['state_clean'] = fips_xw['state'].str.strip().str.upper()

# Apply the same cleaning procedure to the closures dataset
cl['county_clean'] = cl['County/district'].str.strip().str.lower()
cl['state_clean']  = cl['State'].str.strip().str.upper()

# ── STEP 3: MERGE CLOSURES TO FIPS ───────────────────────────────────
# Attempt to match closure records to counties using exact county/state matches.
print("\n-- Merging closures to FIPS --")

merged_cl = cl.merge(
    fips_xw[['name_clean', 'state_clean', 'fips']],
    left_on  = ['county_clean', 'state_clean'],
    right_on = ['name_clean', 'state_clean'],
    how      = 'left'
)

# Report match success rate
matched   = merged_cl['fips'].notna().sum()
unmatched = merged_cl['fips'].isna().sum()

print(f"Matched:   {matched} / {len(merged_cl)}  ({100*matched/len(merged_cl):.1f}%)")
print(f"Unmatched: {unmatched}")

# Display unmatched counties to diagnose issues
if unmatched > 0:
    print("\nUnmatched counties:")
    miss = merged_cl[merged_cl['fips'].isna()][['County/district', 'State', 'Closure Year']]
    print(miss.to_string(index=False))

    # Attempt fuzzy string matching to recover remaining counties
    try:
        from fuzzywuzzy import process
        print("\nAttempting fuzzy matching...")

        fips_lookup = dict(zip(
            fips_xw['name_clean'] + '|' + fips_xw['state_clean'],
            fips_xw['fips']
        ))

        keys = list(fips_lookup.keys())

        for idx, row in merged_cl[merged_cl['fips'].isna()].iterrows():
            query = f"{row['county_clean']}|{row['state_clean']}"
            best, score = process.extractOne(query, keys)

            if score >= 85:
                merged_cl.loc[idx, 'fips'] = fips_lookup[best]
                print(f"  '{query}' -> '{best}' (score={score}) -> FIPS {fips_lookup[best]}")
            else:
                print(f"  '{query}' -> no match found (best score={score})")

    except ImportError:
        print("  (install fuzzywuzzy: pip install fuzzywuzzy python-Levenshtein)")

# ── MANUAL FIPS CORRECTIONS ─────────────────────────────────────────
# Apply targeted corrections for counties that were misclassified
# by fuzzy matching or contain formatting anomalies.
manual_fixes = {
    ('norton',            'VA'): 51720,
    ('sitka,',            'AK'): 2220,
    ('vernon parish',     'LA'): 22115,
    ('st. landry parish', 'LA'): 22097,
}

print("\nApplying manual FIPS corrections...")

for (county, state), fips_val in manual_fixes.items():
    mask = (merged_cl['county_clean'] == county) & (merged_cl['state_clean'] == state)

    if mask.any():
        merged_cl.loc[mask, 'fips'] = fips_val
        print(f"  Fixed: {county}, {state} -> FIPS {fips_val}")
    else:
        print(f"  (not found in data, skipping): {county}, {state}")

# Convert FIPS identifiers to integer format
merged_cl['fips'] = pd.to_numeric(merged_cl['fips'], errors='coerce').astype('Int64')

# ── STEP 4: BUILD CLOSURE VARIABLES ─────────────────────────────────
# Construct county-level closure indicators summarizing hospital
# closure activity within each county.

print("\n-- Building county-year closure variables --")

cl_clean = merged_cl.dropna(subset=['fips'])[
    ['fips', 'Closure Year', 'is_rural_hospital',
     'Complete Closure (0);\nConverted Closure (1)']
].copy()

cl_clean.columns = ['fips', 'closure_year', 'is_rural_hospital', 'closure_type']
cl_clean['fips'] = cl_clean['fips'].astype(int)

# Collapse to county-level summary statistics
ever_cl = (cl_clean[cl_clean['is_rural_hospital'] == 1]
           .groupby('fips')
           .agg(first_closure_year = ('closure_year', 'min'),
                n_closures         = ('closure_year', 'count'),
                any_complete       = ('closure_type', lambda x: (x == 0).any()))
           .reset_index())

# Indicator variables describing closure status
ever_cl['ever_closed']      = 1
ever_cl['complete_closure'] = ever_cl['any_complete'].astype(int)

print(f"Counties with >=1 rural hospital closure: {len(ever_cl)}")
print(f"  Of which complete closures: {ever_cl['complete_closure'].sum()}")

# ── STEP 5: MERGE INTO PANEL ────────────────────────────────────────
# Integrate closure variables into the main county-year panel dataset.
print("\n-- Merging into panel dataset --")

panel = pd.read_csv(PANEL)
panel['fips'] = panel['fips'].astype(int)

panel = panel.merge(
    ever_cl[['fips', 'ever_closed', 'first_closure_year', 'n_closures', 'complete_closure']],
    on='fips', how='left'
)

# Replace missing values for counties with no closures
panel['ever_closed']      = panel['ever_closed'].fillna(0).astype(int)
panel['complete_closure'] = panel['complete_closure'].fillna(0).astype(int)

# Construct time-varying indicator for years after a closure occurs
panel['post_closure'] = np.where(
    (panel['ever_closed'] == 1) & (panel['year'] >= panel['first_closure_year']),
    1, 0
)

# Diagnostics describing closure distribution
print(f"Panel shape: {panel.shape}")
print(f"Counties with ever_closed=1: {panel[panel['ever_closed']==1]['fips'].nunique()}")
print(f"  Rural: {panel[(panel['ever_closed']==1)&(panel['is_rural']==1)]['fips'].nunique()}")
print(f"  Urban: {panel[(panel['ever_closed']==1)&(panel['is_rural']==0)]['fips'].nunique()}")

print(f"\nObs breakdown:")
print(panel.groupby(['is_rural','ever_closed']).size().rename('n_obs'))

# Save enriched panel dataset
panel.to_csv(OUT_CSV, index=False)
print(f"\nSaved enriched panel -> {OUT_CSV}")

# ── STEP 6: REGRESSIONS ─────────────────────────────────────────────
# Estimate additional TWFE regression models testing whether hospital
# closures explain variation in Medicaid expansion effects.

print("\n" + "=" * 60)
print("REGRESSION MODELS")
print("=" * 60)

CONTROLS = ['unemployment_rate', 'median_income', 'uninsured_rate']