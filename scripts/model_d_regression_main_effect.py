import pandas as pd
from linearmodels.panel import PanelOLS
import os

# -------------------------------------------------------------
# ECONOMETRIC ANALYSIS SCRIPT
# Medicaid Expansion and Medical Debt (Panel Fixed Effects)
# -------------------------------------------------------------
# This script estimates the total effect of Medicaid expansion
# on county-level medical debt using a two-way fixed effects
# panel regression model.
#
# Unit of analysis: County-Year
# Panel structure:
#   Entity = County (FIPS code)
#   Time   = Year
#
# The model evaluates whether counties in expansion states
# experienced lower medical debt after Medicaid expansion,
# and whether the effect differs between rural and urban areas.
# -------------------------------------------------------------


# -------------------------------------------------------------
# STEP 1: LOAD CLEANED PANEL DATASET
# -------------------------------------------------------------
# Load the final merged dataset containing county-level
# measures of medical debt, Medicaid expansion status,
# geographic indicators, and economic controls.
base_path = '/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/'
df = pd.read_csv(os.path.join(base_path, 'data/processed/FINAL_DATASET_V13_NO_HOSP.csv'))


# -------------------------------------------------------------
# STEP 2: PREPARE ANALYSIS VARIABLES
# -------------------------------------------------------------

# Create an Urban indicator variable.
# The dataset already includes an 'is_rural' variable, so we
# construct the urban indicator as the complement of that value.
df['is_urban'] = 1 - df['is_rural']

# Convert the dataset into a panel structure by setting a
# multi-index consisting of:
#   - County identifier (fips)
#   - Year
#
# This structure is required by the PanelOLS estimator.
df = df.set_index(['fips', 'year'])


# =============================================================
# MODEL D: TOTAL POLICY EFFECT
# =============================================================
# This specification estimates the total effect of Medicaid
# expansion on medical debt by removing the uninsured_rate
# control variable.
#
# Rationale:
# In earlier specifications, uninsured_rate may act as a
# mediating variable through which Medicaid expansion reduces
# medical debt. Including it would estimate only the direct
# effect of expansion.
#
# By excluding uninsured_rate, this model captures the
# overall policy impact (both direct and indirect effects).
#
# Key components of the model:
#
# medicaid_expansion
#   → Baseline effect of expansion in urban counties.
#
# medicaid_expansion:is_rural
#   → Interaction term capturing whether the expansion
#     effect differs in rural counties relative to urban ones.
#
# unemployment_rate
# median_income
#   → Economic control variables to account for county-level
#     labor market conditions and income differences.
#
# EntityEffects
#   → County fixed effects controlling for time-invariant
#     county characteristics (e.g., baseline healthcare access,
#     demographics, persistent economic structure).
#
# TimeEffects
#   → Year fixed effects controlling for nationwide shocks
#     affecting all counties simultaneously (e.g., policy
#     changes, macroeconomic trends, pandemic shocks).
# =============================================================

formula_total_effect = (
    "share_debt_all ~ "
    "medicaid_expansion + "            # Baseline expansion effect (urban counties)
    "medicaid_expansion:is_rural + "   # Differential effect in rural counties
    "unemployment_rate + "             # Control for local labor market conditions
    "median_income + "                 # Control for county income differences
    "EntityEffects + TimeEffects"      # Two-way fixed effects specification
)


# -------------------------------------------------------------
# STEP 3: ESTIMATE PANEL REGRESSION MODEL
# -------------------------------------------------------------
# Estimate the model using PanelOLS from the linearmodels
# package with clustered standard errors.
#
# Clustered standard errors at the county level account for
# serial correlation within counties over time.

results_total = PanelOLS.from_formula(
    formula_total_effect,
    data=df
).fit(
    cov_type='clustered',
    cluster_entity=True
)


# -------------------------------------------------------------
# STEP 4: PRINT MODEL OUTPUT
# -------------------------------------------------------------
# Display the regression summary in the console to review
# coefficient estimates, standard errors, and model fit
# statistics.

print("=" * 60)
print("MODEL D: TOTAL EFFECT (WITHOUT UNINSURED RATE CONTROL)")
print("=" * 60)
print(results_total.summary)


# -------------------------------------------------------------
# STEP 5: SAVE RESULTS TO FILE
# -------------------------------------------------------------
# Export the regression results to a text file for inclusion
# in the project's results tables or appendix.

output_path = '/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/tables/Model_D_Total_Effect_Results.txt'

with open(output_path, "w") as f:
    f.write("QSS 84: Total Effect of Medicaid Expansion on Medical Debt\n")
    f.write("Specification: TWFE DiD without Uninsured Rate control\n")
    f.write("=" * 60 + "\n")
    f.write(str(results_total.summary))

print(f"\nSuccess! Results saved to {output_path}")