import pandas as pd

# --- STAGE 0: Starting dataset ---
# Load the V10 dataset, which is the version before the final cleaning steps.
# This acts as the baseline so we can see how many observations we began with.
df_v10 = pd.read_csv('/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/data/processed/FINAL_PROJECT_DATASET_V10.csv', low_memory=False)

# Since the analysis only uses the 2012–2023 period, we filter to those years
# and count how many observations are available in the usable time window.
v10_initial = len(df_v10[df_v10['year'] >= 2012])
print(f"1. Initial Observations (2012-2023): {v10_initial}")

# --- STAGE 1 & 2: Final cleaned dataset ---
# Load the final dataset (V13). By this point all cleaning steps and filters
# have already been applied, including missing value removal and variable checks.
df_v13 = pd.read_csv('/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/data/processed/FINAL_DATASET_V13_NO_HOSP.csv')
v13_final = len(df_v13)
print(f"2. Final Observations (After all cleaning): {v13_final}")

# --- CALCULATION ---
# Calculate how many rows were dropped between the initial usable dataset
# and the final cleaned version used for the regression analysis.
total_dropped = v10_initial - v13_final
attrition_rate = (total_dropped / v10_initial) * 100

print(f"\n--- ATTRITION SUMMARY ---")
print(f"Total Rows Removed: {total_dropped}")
print(f"Final Data Retention: {100 - attrition_rate:.2f}%")
