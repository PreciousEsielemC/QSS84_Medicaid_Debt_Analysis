import pandas as pd
import statsmodels.formula.api as smf

"""
ECONOMETRIC ANALYSIS: GEOGRAPHIC INTERACTION & CLINICAL MECHANISM
-----------------------------------------------------------------
This script estimates two regression models examining how Medicaid
expansion relates to county-level medical debt.

Model A: Geographic Interaction Model
-------------------------------------
Tests whether the effect of Medicaid expansion differs across
geographic contexts (Urban, Suburban, Rural). By interacting
the expansion indicator with geographic type, the model evaluates
whether structural constraints in rural areas limit the policy’s
effectiveness.

Model B: Healthcare Access Mechanism
------------------------------------
Tests a potential mechanism linking healthcare access to medical
debt. Preventable hospitalizations are used as a proxy for lack
of access to primary care. The model evaluates whether counties
with higher rates of preventable hospital stays also exhibit
higher levels of medical debt.

Both models include key socioeconomic controls such as income,
unemployment, demographics, and geographic characteristics.
"""

# -------------------------------------------------------------
# STEP 1: LOAD MASTER DATASET
# -------------------------------------------------------------
# Import the final cleaned county-year dataset used for the
# project's empirical analysis.
df = pd.read_csv('/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/data/processed/FINAL_DATASET_V13_MASTER.csv')


# -------------------------------------------------------------
# STEP 2: PRE-PROCESS VARIABLES FOR INTERPRETATION
# -------------------------------------------------------------
# Scale median income so regression coefficients reflect the
# change in medical debt associated with a $10,000 increase in
# county median income rather than a $1 increase.
df['median_income_10k'] = df['median_income'] / 10000

# Define geographic category ordering and ensure "Urban" is the
# baseline comparison group in regression models.
df['geo_type'] = pd.Categorical(
    df['geo_type'],
    categories=['Urban', 'Suburban', 'Rural']
)


# -------------------------------------------------------------
# MODEL A: GEOGRAPHIC INTERACTION MODEL
# -------------------------------------------------------------
# This model estimates whether the relationship between
# Medicaid expansion and medical debt varies across
# geographic contexts.
#
# The interaction term allows the expansion effect to differ
# between Urban, Suburban, and Rural counties.
#
# Control variables account for economic conditions and
# demographic characteristics that may influence medical debt.

print("\n" + "="*30)
print("RUNNING MODEL A: GEOGRAPHIC IMPACT")
print("="*30)

formula_a = 'share_debt_all ~ medicaid_expansion * C(geo_type) + unemployment_rate + median_income_10k + pct_poc + median_age'

model_a = smf.ols(
    formula=formula_a,
    data=df
).fit()

print(model_a.summary())


# -------------------------------------------------------------
# MODEL B: HEALTHCARE ACCESS MECHANISM
# -------------------------------------------------------------
# This model evaluates whether preventable hospitalizations
# are associated with higher levels of medical debt.
#
# Preventable hospital stays serve as a proxy for inadequate
# access to primary care services. If this variable is strongly
# associated with medical debt, it suggests that healthcare
# system access—not just insurance status—may drive debt
# accumulation.
#
# The sample is restricted to years with complete hospitalization
# data to ensure reliable estimates.

# Restrict dataset to years where hospitalization data is available
df_mechanism = df[df['year'] <= 2020].dropna(subset=['preventable_hosp_rate'])

print("\n" + "="*30)
print("RUNNING MODEL B: THE HEALTH MECHANISM")
print("="*30)

formula_b = 'share_debt_all ~ medicaid_expansion + preventable_hosp_rate + unemployment_rate + median_income_10k + C(geo_type) + pct_poc + median_age'

model_b = smf.ols(
    formula=formula_b,
    data=df_mechanism
).fit()

print(model_b.summary())


# -------------------------------------------------------------
# STEP 3: SAVE REGRESSION OUTPUT
# -------------------------------------------------------------
# Export regression summaries to text files so results can be
# easily inserted into the project report or appendix tables.

with open('/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/tables/OLS_regression_results_A_not_in_paper.txt', 'w') as f:
    f.write(model_a.summary().as_text())

with open('/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/tables/OLS_regression_results_B_not_in_paper.txt', 'w') as f:
    f.write(model_b.summary().as_text())

print("\nDone! Results saved to 'regression_results_A.txt' and 'regression_results_B.txt'")