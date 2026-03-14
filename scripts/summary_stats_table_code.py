import pandas as pd
import os

# Define local directory for the processed data files
path = '/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/data/processed/'

# Load both datasets: V13_NO_HOSP for primary demographics and V13_MASTER for clinical data [cite: 99, 101]
df_main = pd.read_csv(os.path.join(path, 'FINAL_DATASET_V13_NO_HOSP.csv'))
df_hosp = pd.read_csv(os.path.join(path, 'FINAL_DATASET_V13_MASTER.csv'))

# List of economic and demographic covariates to summarize from the full panel [cite: 88, 133]
main_vars = ['share_debt_all', 'median_income', 'unemployment_rate', 'uninsured_rate', 'pct_poc']

# Calculate means and standard deviations for main variables grouped by rural status [cite: 132, 137]
table_1 = df_main.groupby('is_rural')[main_vars].agg(['mean', 'std']).T

# Calculate means and standard deviations for the clinical mechanism variable [cite: 102, 140]
hosp_stats = df_hosp.groupby('is_rural')[['preventable_hosp_rate']].agg(['mean', 'std']).T

# Combine both sets of results into a single composite table for the report [cite: 102, 138]
final_table_1 = pd.concat([table_1, hosp_stats]).round(3)
final_table_1.columns = ['Urban (0)', 'Rural (1)']

# Output the formatted Table 1 to the terminal for verification [cite: 137]
print("--- FINAL TABLE 1: SUMMARY STATISTICS (2012-2023) ---")
print(final_table_1)

# Export the summary statistics to a CSV for use in the final paper [cite: 139, 140]
final_table_1.to_csv('/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/tables/summary_stats_Table_1.csv')