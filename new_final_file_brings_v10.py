import pandas as pd
import glob
import os
import re

# 1. SETUP
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def bulletproof_cleaner_v10(file_path, table_type):
    try:
        df = pd.read_csv(file_path, low_memory=False)
        fname = os.path.basename(file_path)
        year = int(re.search(r'20\d{2}', fname).group())
        labels = df.iloc[0]
        target_cols = {}

        for col in df.columns:
            if pd.isna(labels[col]): continue
            lbl = str(labels[col]).lower()

            # --- INCOME (S1903) ---
            if table_type == 'income':
                if 'median income' in lbl and 'household' in lbl and 'estimate' in lbl:
                    if 'margin' not in lbl and 'race' not in lbl and 'age' not in lbl:
                        if 'median_income' not in target_cols: target_cols['median_income'] = col

            # --- DEMOGRAPHICS (DP05) - Fixed for 2017/2018 Gaps ---
            elif table_type == 'demo':
                # Race
                if 'white alone' in lbl and 'not hispanic' in lbl and 'percent' in lbl:
                    if 'margin' not in lbl: target_cols['pct_white_non_hisp'] = col
                # Median Age (Loosened filter to catch 2017-2018)
                if 'median age' in lbl and 'estimate' in lbl:
                    if 'margin' not in lbl and 'male' not in lbl and 'female' not in lbl:
                        if 'median_age' not in target_cols: target_cols['median_age'] = col
                # 65+ Percent
                if '65 years' in lbl and 'percent' in lbl:
                    if 'margin' not in lbl and 'male' not in lbl and 'female' not in lbl:
                        if 'pct_65_plus' not in target_cols: target_cols['pct_65_plus'] = col

            # --- ECONOMICS (DP03) - Fixed for 2011 Gap ---
            elif table_type == 'econ':
                # Captures the old 2011 "Percent!!Unemployed" format
                if 'unemploy' in lbl and 'percent' in lbl:
                    if 'labor' in lbl and 'margin' not in lbl and 'female' not in lbl:
                        if 'unemployment_rate' not in target_cols: target_cols['unemployment_rate'] = col

        if target_cols:
            clean = df.drop(0)[['GEO_ID'] + list(target_cols.values())].copy()
            clean = clean.rename(columns={v: k for k, v in target_cols.items()})
            clean['fips'] = clean['GEO_ID'].str[-5:]
            clean['year'] = year
            for c in target_cols.keys(): clean[c] = pd.to_numeric(clean[c], errors='coerce')
            return clean[['fips', 'year'] + list(target_cols.keys())]
    except Exception as e: print(f"Error in {fname}: {e}")
    return None

# --- RUN CLEANING ---
targets = {'income': 'S1903', 'demo': 'DP05', 'econ': 'DP03'}
for key, table_id in targets.items():
    files = [f for f in glob.glob(f"**/*{table_id}*Data.csv", recursive=True) if "5Y" in f]
    print(f"Cleaning {key} ({len(files)} files)...")
    processed = [bulletproof_cleaner_v10(f, key) for f in files]
    pd.concat([d for d in processed if d is not None], ignore_index=True).to_csv(f"cleaned_{key}_v10.csv", index=False)

# --- MASTER MERGE ---
df_inc = pd.read_csv('cleaned_income_v10.csv', dtype={'fips': str})
df_ec = pd.read_csv('cleaned_econ_v10.csv', dtype={'fips': str})
df_dem = pd.read_csv('cleaned_demo_v10.csv', dtype={'fips': str})
df_ins = pd.read_csv('cleaned_insurance_master_final.csv', dtype={'fips': str})
df_debt_raw = pd.read_csv('Urban_Institute_data_1.csv', dtype={'fips': str})

# 1. Standardize FIPS (5-digits)
for df in [df_inc, df_ec, df_dem, df_ins, df_debt_raw]:
    df['fips'] = df['fips'].astype(str).str.zfill(5)

# 2. Reshape Debt
df_long = pd.melt(df_debt_raw[df_debt_raw['metric'] == 'share_debt_all'],
                  id_vars=['fips', 'full_name'], value_vars=[str(y) for y in range(2011, 2024)],
                  var_name='year', value_name='share_debt_all')
df_long['year'] = df_long['year'].astype(int)

# 3. Join
final = pd.merge(df_long, df_inc, on=['fips', 'year'], how='left')
final = pd.merge(final, df_ec, on=['fips', 'year'], how='left')
final = pd.merge(final, df_dem, on=['fips', 'year'], how='left')
final = pd.merge(final, df_ins, on=['fips', 'year'], how='left')

# 4. Filter out State/US rows (Keep only real counties)
final = final[final['full_name'].str.contains(',', na=False)]

# 5. Policy & POC Math
expansion_map = {"02": 2015, "04": 2014, "05": 2014, "06": 2014, "08": 2014, "09": 2014, "10": 2014, "11": 2014, "15": 2014, "16": 2020, "17": 2014, "18": 2015, "19": 2014, "21": 2014, "22": 2016, "23": 2019, "24": 2014, "25": 2014, "26": 2014, "27": 2014, "29": 2021, "30": 2016, "31": 2020, "32": 2014, "33": 2014, "34": 2014, "35": 2014, "36": 2014, "37": 2023, "38": 2014, "39": 2014, "40": 2021, "41": 2014, "42": 2015, "44": 2014, "46": 2023, "49": 2020, "50": 2014, "51": 2019, "53": 2014, "54": 2014}
final['medicaid_expansion'] = final.apply(lambda x: 1 if x['fips'][:2] in expansion_map and x['year'] >= expansion_map[x['fips'][:2]] else 0, axis=1)
final['pct_poc'] = 100 - final['pct_white_non_hisp']

# EXPORT
final.to_csv('FINAL_PROJECT_DATASET_V10.csv', index=False)
final.to_excel('FINAL_PROJECT_DATASET_V10.xlsx', index=False, engine='openpyxl')
print("\n--- VERSION 10 COMPLETE ---")
print("Cleaned: FIPS zeros, State-level rows, and 2011/2017/2018 gaps.")