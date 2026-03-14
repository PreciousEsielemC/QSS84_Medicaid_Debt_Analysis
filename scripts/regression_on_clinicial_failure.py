import statsmodels.formula.api as smf
import pandas as pd

# Pulling in the final V13 master dataset for the mechanism test
df = pd.read_csv('/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/data/processed/FINAL_DATASET_V13_MASTER.csv')

# Running a cross-sectional OLS to check the link between clinical failure and debt
# Testing if preventable hospitalizations significantly predict higher debt shares
model = smf.ols('share_debt_all ~ preventable_hosp_rate + median_income + uninsured_rate', data=df).fit()

# View the coefficients and p-values for the mechanism discussion
print(model.summary())