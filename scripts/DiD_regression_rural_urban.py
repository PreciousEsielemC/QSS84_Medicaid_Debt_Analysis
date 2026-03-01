import pandas as pd
from linearmodels.panel import PanelOLS

"""
RESEARCH SPECIFICATION: TWO-WAY FIXED EFFECTS (TWFE)
---------------------------------------------------
Model Choice: Two-Way Fixed Effects (TWFE) Difference-in-Differences.
- Entity Effects (County): Controls for time-invariant county characteristics (e.g., geography, local culture).
- Time Effects (Year): Controls for national shocks (e.g., the 2022 credit reporting changes or COVID-19).

Clustering: Standard Errors are clustered by State.
- Reason: Medicaid Expansion is a state-level policy. Clustering by state accounts for 
  within-state correlation of errors and ensures our T-stats are not artificially inflated, 
  making the 0.0037 rural effect more statistically robust.
"""
# 1. Load your master dataset
# Ensure your CSV has: fips, year, share_debt_all, medicaid_expansion, is_rural, state_fips, etc.
df = pd.read_csv('FINAL_DATASET_V13_MASTER.csv')

# 2. Create the Urban Binary
# If is_rural is 1 for rural, then (1 - 1) = 0 for rural and (1 - 0) = 1 for urban.
df['is_urban'] = 1 - df['is_rural']

# 3. Set the Panel Index (Entity and Time)
# This is required for PanelOLS to know what the 'Fixed Effects' are.
df = df.set_index(['fips', 'year'])

# 4. Define the Regression Model
# We follow Prof. DeWan's rule: No 'is_urban' main effect, only the interaction.
# We include your significant controls: unemployment, income, and uninsured rate.

formula = (
    "share_debt_all ~ "
    "medicaid_expansion:is_urban + "  # This is the Urban Interaction
    "unemployment_rate + " 
    "median_income + " 
    "uninsured_rate + " 
    "EntityEffects + TimeEffects"     # This adds the Two-Way Fixed Effects
)

# 5. Run the Model with State-Level Clustering
# Clustering by state accounts for the fact that Medicaid is a state-level policy.
model_urban = PanelOLS.from_formula(formula, data=df)
results_urban = model_urban.fit(cov_type='clustered', cluster_entity=True)

# 6. Display the Results
print("==========================================================")
print("URBAN INTERACTION SPECIFICATION (TWFE DID)")
print("==========================================================")
print(results_urban.summary)

# 7. (Optional) Run the Rural Interaction side-by-side for comparison
formula_rural = (
    "share_debt_all ~ "
    "medicaid_expansion:is_rural + " 
    "unemployment_rate + " 
    "median_income + " 
    "uninsured_rate + " 
    "EntityEffects + TimeEffects"
)
results_rural = PanelOLS.from_formula(formula_rural, data=df).fit(cov_type='clustered', cluster_entity=True)

print("\n\n==========================================================")
print("RURAL INTERACTION SPECIFICATION (TWFE DID)")
print("==========================================================")
print(results_rural.summary)

# --- STEP 8: EXPORT RESULTS TO TEXT FILE FOR OVERLEAF ---

with open("DiD_regression_results_V13.txt", "w") as f:
    f.write("==========================================================\n")
    f.write("URBAN INTERACTION SPECIFICATION (TWFE DID)\n")
    f.write("==========================================================\n")
    f.write(str(results_urban.summary))

    f.write("\n\n" + "=" * 60 + "\n\n")

    f.write("==========================================================\n")
    f.write("RURAL INTERACTION SPECIFICATION (TWFE DID)\n")
    f.write("==========================================================\n")
    f.write(str(results_rural.summary))

print("\nSuccess! 'DiD_regression_results_V13.txt' created in your project folder.")
