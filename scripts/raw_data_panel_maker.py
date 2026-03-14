import pandas as pd
import glob
import os
import re
import seaborn as sns
import matplotlib.pyplot as plt

# -------------------------------------------------------------
# STEP 1: DEFINE DIRECTORY STRUCTURE
# -------------------------------------------------------------
# Set the base project directory and define paths for the
# raw data sources and processed output files.
base_path = '/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/data/'
raw_path = os.path.join(base_path, 'raw/')
processed_path = os.path.join(base_path, 'processed/')

# Ensure that the processed data directory exists.
# If it does not exist, create it automatically.
if not os.path.exists(processed_path):
    os.makedirs(processed_path)


# -------------------------------------------------------------
# STEP 2: LOAD AND CLEAN MEDICAL DEBT DATA
# -------------------------------------------------------------
# Import the Urban Institute medical debt dataset. The dataset
# contains multiple metrics across years in wide format.
print("Loading Debt data...")
df_debt_raw = pd.read_csv(os.path.join(raw_path, 'Urban_Institute_data_1.csv'))

# Convert the dataset from wide format (years as columns)
# into long format with one row per county-year observation.
df_debt = df_debt_raw.melt(
    id_vars=['fips', 'full_name', 'metric'],
    var_name='year',
    value_name='debt_val'
)

# Filter the dataset to retain only the primary metric used
# in the analysis: the share of residents with medical debt.
df_debt = df_debt[df_debt['metric'] == 'share_debt_all']

# Standardize FIPS codes so that they are always 5 digits,
# ensuring compatibility with Census county identifiers.
df_debt['fips'] = df_debt['fips'].astype(str).str.zfill(5)

# Convert the year variable to numeric format for merging
# and time-based analysis.
df_debt['year'] = pd.to_numeric(df_debt['year'], errors='coerce')


# -------------------------------------------------------------
# STEP 3: DYNAMICALLY LOAD CENSUS DATA FILES
# -------------------------------------------------------------
# The raw folder may contain many ACS Census tables from
# different years and table types. This section automatically
# searches the directory and loads relevant variables.

census_frames = []

# Recursively search the raw data directory for all CSV files.
all_files = glob.glob(os.path.join(raw_path, "**/*.csv"), recursive=True)

print(f"Found {len(all_files)} total files in the raw directory.")

for file_path in all_files:
    try:
        # Standardize filename formatting for easier pattern matching
        fname = os.path.basename(file_path).lower()

        # Skip metadata files or non-CSV files
        if 'metadata' in fname or not fname.endswith('.csv'):
            continue

        # Skip the Urban Institute debt file (already loaded above)
        if 'urban_institute' in fname:
            continue

        # Extract the year from the filename using regex
        year_match = re.search(r'20\d{2}', fname)
        if not year_match:
            continue
        year = int(year_match.group())

        # Load the current Census file
        df_temp = pd.read_csv(file_path, low_memory=False)

        # Skip files that contain no data
        if df_temp.empty:
            continue

        # ---------------------------------------------------------
        # DATA CLEANING: COLUMN LABEL EXTRACTION
        # ---------------------------------------------------------
        # ACS tables typically include a descriptive header row
        # containing variable labels. We store these labels to
        # identify relevant variables programmatically.
        labels = df_temp.iloc[0].fillna('').astype(str).str.lower()

        # Remove the label row from the dataset
        df_temp = df_temp.drop(0)

        # Initialize dictionary mapping raw column names
        # to standardized variable names
        target_cols = {'GEO_ID': 'fips'}

        # ---------------------------------------------------------
        # VARIABLE IDENTIFICATION LOGIC
        # ---------------------------------------------------------
        # Automatically detect relevant economic variables
        # from ACS tables using keyword matching.

        for col in df_temp.columns:

            lbl = labels[col]
            if not lbl:
                continue

            # 1. Median Household Income (ACS Table S1903)
            if 's1903' in fname:
                if 'median income' in lbl and 'household' in lbl and 'estimate' in lbl:
                    if 'margin' not in lbl and 'race' not in lbl and 'age' not in lbl:
                        target_cols[col] = 'median_income'

            # 2. Economic Characteristics (ACS Table DP03)
            elif 'dp03' in fname:

                # Unemployment rate (percent of labor force)
                if 'unemploy' in lbl and 'percent' in lbl and 'labor' in lbl:
                    if 'margin' not in lbl:
                        target_cols[col] = 'unemployment'

                # Share of population without health insurance
                if 'no health insurance' in lbl and 'percent' in lbl:
                    if 'margin' not in lbl:
                        target_cols[col] = 'uninsured'

        # ---------------------------------------------------------
        # BUILD CLEAN DATAFRAME FOR THIS FILE
        # ---------------------------------------------------------
        # Only proceed if at least one variable of interest
        # (beyond the FIPS identifier) was successfully detected.
        if len(target_cols) > 1:

            df_clean = df_temp[list(target_cols.keys())].copy()

            # Rename columns to standardized variable names
            df_clean.columns = [target_cols.get(col, col) for col in df_clean.columns]

            # Standardize FIPS codes
            df_clean['fips'] = df_clean['fips'].astype(str).str[-5:]

            # Add the year extracted from the filename
            df_clean['year'] = year

            # Remove duplicated columns if they appear
            df_clean = df_clean.loc[:, ~df_clean.columns.duplicated()].copy()

            # Store cleaned dataset for later merging
            census_frames.append(df_clean)

    except Exception as e:

        # If any file fails to process, skip it but continue
        print(f"Skipping {os.path.basename(file_path)}: {e}")


# -------------------------------------------------------------
# STEP 4: MERGE DATA AND GENERATE PANEL DATASET
# -------------------------------------------------------------
# Combine all successfully extracted Census dataframes
# into a single county-year dataset.

if not census_frames:

    print("CRITICAL: No census frames were created. Check folder structure.")

else:

    print("Merging data...")

    # Concatenate all extracted Census data
    df_all_census = pd.concat(census_frames, ignore_index=True)

    # Collapse duplicates so each county-year appears once
    df_all_census = df_all_census.groupby(['fips', 'year']).first().reset_index()

    # ---------------------------------------------------------
    # FINAL MASTER MERGE
    # ---------------------------------------------------------
    # Merge the Census data with the Urban Institute
    # medical debt dataset to create the final panel.
    df_master = df_debt.merge(df_all_census, on=['fips', 'year'], how='inner')

    # ---------------------------------------------------------
    # DATA TYPE CONVERSION
    # ---------------------------------------------------------
    # Convert key variables to numeric format to ensure
    # they are usable in statistical analysis.
    cols = ['median_income', 'unemployment', 'uninsured', 'debt_val']

    for c in cols:
        if c in df_master.columns:
            df_master[c] = pd.to_numeric(df_master[c], errors='coerce')

    # ---------------------------------------------------------
    # DESCRIPTIVE STATISTICS
    # ---------------------------------------------------------
    # Display summary statistics for the main variables
    # used in the panel dataset.
    print("\n--- Summary Statistics (2012-2023 Panel) ---")
    print(df_master[cols].describe().T)

    # ---------------------------------------------------------
    # SAVE FINAL PANEL DATASET
    # ---------------------------------------------------------
    # Export the cleaned and merged county-year dataset
    # for use in regression and visualization scripts.
    df_master.to_csv(
        os.path.join(processed_path, 'raw_data_test_look.csv'),
        index=False
    )

    print(f"\nSaved master panel to: {os.path.join(processed_path, 'raw_data_test_look.csv')}")