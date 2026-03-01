import pandas as pd
import glob
import seaborn as sns
import matplotlib.pyplot as plt
import os

# --- 1. PROCESS URBAN INSTITUTE DEBT DATA (2011-2023) ---
# This file contains the longitudinal outcome variable
df_debt_raw = pd.read_csv('Urban_Institute_data_1.csv')
df_debt = df_debt_raw.melt(id_vars=['fips', 'full_name', 'metric'], 
                           var_name='year', value_name='debt_val')

# Filter for the specific dependent variable: Share with Medical Debt
df_debt = df_debt[df_debt['metric'] == 'share_debt_all']
df_debt['fips'] = df_debt['fips'].astype(str).str.zfill(5)
df_debt['year'] = df_debt['year'].astype(int)
df_debt['state_name'] = df_debt['full_name'].str.split(', ').str[-1]

# --- 2. PROCESS MEDICAID EXPANSION (KFF) ---
# This is your primary 'Policy Buffer' control
df_medicaid = pd.read_csv('medicaid_expansion_kff.csv', skiprows=2)
df_medicaid['Exp_Year'] = pd.to_datetime(df_medicaid['Expansion Implementation Date'], errors='coerce').dt.year

# --- 3. DYNAMICALLY LOAD ALL CENSUS FILES ---
# This loop finds all S1903, DP03, and DP05 files in your current folder
census_frames = []
pattern = "*Data.csv" # Matches the naming convention of your uploaded files

for file_path in glob.glob(pattern):
    # Extract the year from the filename (e.g., '2011' from 'ACSDP1Y2011.DP05-Data.csv')
    try:
        year_str = ''.join(filter(str.isdigit, os.path.basename(file_path)))
        year = int(year_str[4:8]) 
    except:
        continue

    # Skip the metadata row
    df_temp = pd.read_csv(file_path).drop(0) 
    df_temp['fips'] = df_temp['GEO_ID'].str[-5:]
    df_temp['year'] = year
    
    # Mapping the specific columns we identified from your uploads
    # S1903: Median Income
    # DP03: Uninsured and Unemployment
    cols_to_keep = {'fips': 'fips', 'year': 'year'}
    if 'S1903' in file_path: cols_to_keep['S1903_C02_001E'] = 'median_income'
    if 'DP03' in file_path: 
        cols_to_keep['DP03_0009PE'] = 'unemployment'
        cols_to_keep['DP03_0099PE'] = 'uninsured'
    if 'DP05' in file_path:
        cols_to_keep['DP05_0072PE'] = 'pct_white'

    # Filter for valid columns and add to list
    existing_cols = [c for c in cols_to_keep.keys() if c in df_temp.columns]
    census_frames.append(df_temp[existing_cols].rename(columns=cols_to_keep))

# Merge all census years into one dataframe
df_all_census = pd.concat(census_frames).apply(pd.to_numeric, errors='ignore')

# --- 4. MASTER MERGE ---
# Merging debt, census, and medicaid implementation data
df_master = df_debt.merge(df_all_census, on=['fips', 'year'], how='inner')
df_master = df_master.merge(df_medicaid[['Location', 'Exp_Year']], 
                            left_on='state_name', right_on='Location')

# Create the binary control: 1 if year is after expansion, else 0
df_master['is_expanded'] = (df_master['year'] >= df_master['Exp_Year']).astype(int)

# --- 5. GENERATE (5) SUMMARY STATISTICS ---
print("\n--- Summary Statistics (Longitudinal Panel) ---")
print(df_master[['median_income', 'debt_val', 'uninsured', 'unemployment']].describe().T)

# --- 6. VISUALIZATIONS ---
# Visualization for H1: Correlation Scatter
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df_master, x='median_income', y='debt_val', alpha=0.3)

plt.title('National Correlation: Median Income vs. Medical Debt (2011-2023)')
plt.show()

# Visualization for H3: Divergence Trend
plt.figure(figsize=(10, 6))
sns.lineplot(data=df_master, x='year', y='debt_val', hue='is_expanded')

plt.title('Longitudinal Debt Trends: Medicaid Expansion vs. Non-Expansion')
plt.show()
