import pandas as pd

# --- STAGE 0: The True Starting Point ---
df_v10 = pd.read_csv('FINAL_PROJECT_DATASET_V10.csv', low_memory=False)
# Since your study is 2012-2023, we filter for that first
v10_initial = len(df_v10[df_v10['year'] >= 2012])
print(f"1. Initial Observations (2012-2023): {v10_initial}")

# --- STAGE 1 & 2: The Final Result ---
df_v13 = pd.read_csv('FINAL_DATASET_V13_MASTER.csv')
v13_final = len(df_v13)
print(f"2. Final Observations (After all cleaning): {v13_final}")

# --- CALCULATION ---
total_dropped = v10_initial - v13_final
attrition_rate = (total_dropped / v10_initial) * 100

print(f"\n--- ATTRITION SUMMARY ---")
print(f"Total Rows Removed: {total_dropped}")
print(f"Final Data Retention: {100 - attrition_rate:.2f}%")
