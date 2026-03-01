import pandas as pd
import statsmodels.formula.api as smf

"""
MODEL SPECIFICATION: GEOGRAPHIC INTERACTION & CLINICAL MECHANISM
--------------------------------------------------------------
Model A: Tests for geographic divergence. By interacting Medicaid Expansion with Rural/Urban 
status, we quantify the 'Rural Friction'—the extent to which rural infrastructure 
impedes policy effectiveness.

Model B: Tests the clinical mechanism. This model treats 'Preventable Hospitalizations' 
as a proxy for healthcare access. It evaluates if lack of primary care (leading to hospital stays) 
is a primary driver of medical debt accumulation, regardless of insurance status.
"""
# 1. Load your Master Dataset
df = pd.read_csv('FINAL_DATASET_V13_MASTER.csv')

# 2. Pre-Processing for Research Quality
# We scale Median Income by 10,000 so the result is "Debt change per $10k increase"
df['median_income_10k'] = df['median_income'] / 10000

# Set 'Urban' as the baseline for comparison
df['geo_type'] = pd.Categorical(df['geo_type'], categories=['Urban', 'Suburban', 'Rural'])

# --- MODEL A: THE GEOGRAPHIC INTERACTION (2012-2023) ---
# This tests if the policy worked differently in Rural vs Urban areas
print("\n" + "="*30)
print("RUNNING MODEL A: GEOGRAPHIC IMPACT")
print("="*30)

formula_a = 'share_debt_all ~ medicaid_expansion * C(geo_type) + unemployment_rate + median_income_10k + pct_poc + median_age'
model_a = smf.ols(formula=formula_a, data=df).fit()
print(model_a.summary())


# --- MODEL B: THE CLINICAL MECHANISM (2012-2020) ---
# This tests if preventable hospital stays are the "reason" for debt
# We filter for years <= 2020 because that is where the hospital data is complete
df_mechanism = df[df['year'] <= 2020].dropna(subset=['preventable_hosp_rate'])

print("\n" + "="*30)
print("RUNNING MODEL B: THE HEALTH MECHANISM")
print("="*30)

formula_b = 'share_debt_all ~ medicaid_expansion + preventable_hosp_rate + unemployment_rate + median_income_10k + C(geo_type) + pct_poc + median_age'
model_b = smf.ols(formula=formula_b, data=df_mechanism).fit()
print(model_b.summary())

# --- SAVE RESULTS TO TEXT FILES ---
# This is helpful for copying results into your paper
with open('OLS_regression_results_A.txt', 'w') as f:
    f.write(model_a.summary().as_text())

with open('OLS_regression_results_B.txt', 'w') as f:
    f.write(model_b.summary().as_text())

print("\nDone! Results saved to 'regression_results_A.txt' and 'regression_results_B.txt'")
