import pandas as pd

# 1. Load your final balanced panel dataset
df = pd.read_csv('FINAL_DATASET_V12_MASTER.csv')

# 2. Define the key variables
variables_of_interest = [
    'share_debt_all',
    'uninsured_rate',
    'preventable_hosp_rate',
    'unemployment_rate',
    'median_income'
]

# 3. Calculate stats for Urban (is_rural == 0) and Rural (is_rural == 1)
urban_stats = df[df['is_rural'] == 0][variables_of_interest].agg(['mean', 'std', 'median']).T
rural_stats = df[df['is_rural'] == 1][variables_of_interest].agg(['mean', 'std', 'median']).T

# 4. Combine them into one clean table
summary_table = pd.concat([urban_stats, rural_stats], axis=1)

# 5. Rename columns for clarity
summary_table.columns = [
    'Urban Mean', 'Urban Std', 'Urban Median',
    'Rural Mean', 'Rural Std', 'Rural Median'
]

print("==========================================================")
print("TABLE 1: DESCRIPTIVE STATISTICS BY GEOGRAPHIC CLASSIFICATION")
print("==========================================================")
print(summary_table.round(4))

# 6. Export to CSV
summary_table.to_csv('Table1_Summary_Statistics.csv')
