import statsmodels.formula.api as smf
import pandas as pd
# Load data
df = pd.read_csv('FINAL_DATASET_V13_MASTER.csv')
model = smf.ols('share_debt_all ~ preventable_hosp_rate + median_income + uninsured_rate', data=df).fit()
print(model.summary())
