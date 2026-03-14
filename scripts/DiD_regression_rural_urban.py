import pandas as pd
from linearmodels.panel import PanelOLS

"""
RESEARCH SPECIFICATION: TWO-WAY FIXED EFFECTS (TWFE)
-----------------------------------------------------
Model Choice: Two-Way Fixed Effects Difference-in-Differences.

- County Fixed Effects (EntityEffects):
  These absorb characteristics that do not change over time within a county
  (for example geography, long-run economic structure, or local institutions).

- Year Fixed Effects (TimeEffects):
  These capture nationwide shocks that affect all counties in a given year,
  such as COVID-19 or the 2022 credit reporting policy changes.

Clustering of Standard Errors:
Standard errors are clustered at the county level.

Why cluster?
Medicaid expansion is implemented at the state level, which means counties
within the same state may share correlated shocks. Clustering prevents
standard errors from being artificially small and gives more reliable
statistical inference.
"""

# --- STEP 1: LOAD DATA ---
# Load the final cleaned dataset used for the main regressions
df = pd.read_csv(
    '/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/'
    'data/processed/FINAL_DATASET_V13_NO_HOSP.csv'
)

# --- STEP 2: CREATE URBAN INDICATOR ---
# Convert the rural indicator into an urban one.
# If is_rural = 1 → is_urban = 0
# If is_rural = 0 → is_urban = 1
df['is_urban'] = 1 - df['is_rural']

# --- STEP 3: DEFINE PANEL STRUCTURE ---
# PanelOLS requires a multi-index identifying the panel unit (county)
# and the time dimension (year).
df = df.set_index(['fips', 'year'])

# ==========================================================================
# MODEL A: URBAN INTERACTION
# This model estimates the Medicaid expansion effect specifically for
# urban counties. Think of this as the urban baseline effect.
# ==========================================================================
formula_urban = (
    "share_debt_all ~ "
    "medicaid_expansion:is_urban + "   # Interaction term capturing the
                                       # expansion effect in urban counties.
                                       # We omit the main urban term because
                                       # it does not vary over time and is
                                       # absorbed by county fixed effects.
    "unemployment_rate + "
    "median_income + "
    "uninsured_rate + "
    "EntityEffects + TimeEffects"
)

results_urban = PanelOLS.from_formula(formula_urban, data=df).fit(
    cov_type='clustered', cluster_entity=True
)

print("=" * 60)
print("MODEL A: URBAN INTERACTION SPECIFICATION (TWFE DiD)")
print("=" * 60)
print(results_urban.summary)

# ==========================================================================
# MODEL B: RURAL INTERACTION
# This model estimates the expansion effect in rural counties.
# It is used to test whether rural areas experience a different
# outcome from the policy (the hypothesized "rural friction").
# ==========================================================================
formula_rural = (
    "share_debt_all ~ "
    "medicaid_expansion:is_rural + "   # Interaction capturing the
                                       # expansion effect in rural counties
    "unemployment_rate + "
    "median_income + "
    "uninsured_rate + "
    "EntityEffects + TimeEffects"
)

results_rural = PanelOLS.from_formula(formula_rural, data=df).fit(
    cov_type='clustered', cluster_entity=True
)

print("\n" + "=" * 60)
print("MODEL B: RURAL INTERACTION SPECIFICATION (TWFE DiD)")
print("=" * 60)
print(results_rural.summary)

# ==========================================================================
# MODEL C: COMBINED POLICY GAP
# This specification includes both the main expansion effect and the
# rural interaction. The main effect represents the urban baseline,
# while the interaction shows how the rural effect differs from urban.
#
# In other words, this model directly tests whether Medicaid expansion
# works differently in rural versus urban counties.
# ==========================================================================
formula_combined = (
    "share_debt_all ~ "
    "medicaid_expansion + "            # Baseline expansion effect
                                       # (interpreted as the urban effect)
    "medicaid_expansion:is_rural + "   # Additional effect for rural counties
    "unemployment_rate + "
    "median_income + "
    "uninsured_rate + "
    "EntityEffects + TimeEffects"
)

results_combined = PanelOLS.from_formula(formula_combined, data=df).fit(
    cov_type='clustered', cluster_entity=True
)

print("\n" + "=" * 60)
print("MODEL C: COMBINED POLICY GAP (MAIN + RURAL INTERACTION)")
print("=" * 60)
print(results_combined.summary)

# --- STEP 4: SAVE RESULTS FOR LATEX / OVERLEAF ---
# Export the regression summaries to a text file so they can easily
# be copied into tables or appended to the research report.
output_path = "/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/tables/DiD_regression_results_V13.txt"
with open(output_path, "w") as f:
    f.write("QSS 84: Medicaid Expansion & Medical Debt — TWFE DiD Results\n")
    f.write("=" * 60 + "\n\n")

    f.write("MODEL A: URBAN INTERACTION SPECIFICATION (TWFE DiD)\n")
    f.write("=" * 60 + "\n")
    f.write(str(results_urban.summary))
    f.write("\n\n")

    f.write("MODEL B: RURAL INTERACTION SPECIFICATION (TWFE DiD)\n")
    f.write("=" * 60 + "\n")
    f.write(str(results_rural.summary))
    f.write("\n\n")

    f.write("MODEL C: COMBINED POLICY GAP (MAIN + RURAL INTERACTION)\n")
    f.write("=" * 60 + "\n")
    f.write(str(results_combined.summary))

print(f"\nSuccess! '{output_path}' created in your project folder.")