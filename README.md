# QSS82: Medicaid Expansion and the Rural Friction Gap

## Geographic Disparities in Medical Debt: The "Rural Friction" of Medicaid Expansion

**Author:** Precious Esielem  
**Institution:** Dartmouth College, Department of Quantitative Social Science  
**Date:** March 2026  

---

# Project Overview

This research investigates geographic disparities in the impact of the Affordable Care Act's Medicaid expansion on medical debt. Specifically, it evaluates the **"Rural Friction Gap"**: the theory that structural deficits in rural healthcare infrastructure (high preventable hospitalizations and provider shortages) diminish the financial protections typically provided by insurance expansion.

---

# Final Analytical Finding

Using a **Two-Way Fixed Effects (TWFE)** model on a panel of **35,868 county-year observations (2012–2023)**, this study identifies a statistically significant **relative penalty for rural counties**.

While Medicaid expansion provides financial relief via increased insurance coverage, it is associated with a:

**0.73 – 0.90 percentage point relative increase in medical debt shares in rural counties compared to urban counties**  
*(p < 0.001)*

This pattern reflects a **"Discovery Effect"**, where newly insured rural residents begin seeking treatment for previously unmet medical needs, generating formal medical debt within a strained healthcare system.

---

# Data Sources

The project integrates multiple national datasets:

- **Urban Institute** – County-level medical debt in collections (2011–2023)
- **U.S. Census Bureau (ACS 5-Year)** – Socioeconomic controls  
  - S1903  
  - DP03  
  - DP05  
  - B27001
- **Kaiser Family Foundation (KFF)** – State Medicaid expansion adoption dates
- **USDA Economic Research Service** – Rural-Urban Continuum Codes (RUCC 2013)
- **Chartis Center for Rural Health** – Rural hospital closure database
- **AHRQ / County Health Rankings** – Preventable Hospitalization Rates (mechanism variable)

---

# Repository Structure
data
/raw
Original source files

/processed
Cleaned analytical panels
- V13_MASTER
- V13_NO_HOSP
- V14_CLOSURES

/scripts
Python scripts for data cleaning, modeling, and visualization

/tables
Regression outputs and summary statistics

/figures
Event-study plots, maps, and heterogeneity charts


---

# Replication Steps

## 1. Environment Setup

Requires **Python 3.12**

Install dependencies:

```bash
pip install pandas numpy statsmodels linearmodels matplotlib seaborn

2. Data Processing and Cleaning

Run scripts in the following order to reproduce the final analytical sample
(N = 35,868)

scripts/fix_econ_cleaner.py
    ➜ cleaned_econ_v10.csv

scripts/new_final_file_creates_v10.py
    ➜ cleaned_demo_v10.csv
    ➜ cleaned_income_v10.csv
    ➜ cleaned_insurance_v10.csv
    ➜ FINAL_PROJECT_DATASET_V10.csv/.xlsx

scripts/creates_version_11_final.py
    ➜ FINAL_DATASET_V11_CLEAN.csv/.xlsx

scripts/final_litewise_deletion_and_produces_final_dataset_v13.py
    ➜ FINAL_DATASET_V13_MASTER.csv/.xlsx

scripts/hospital_closure_intergration.py
    ➜ FINAL_DATASET_V14_CLOSURES.csv
    ➜ county_fips_crosswalk.csv

scripts/Final_dataset_v13_no_hosp.py
    ➜ FINAL_DATASET_V13_NO_HOSP.csv/.xlsx


3. Analysis and Visualization
Regression Models

Main Results (Models A, B, C)
Run:
scripts/DiD_regression_rural_urban.py
Output:
DiD_regression_results_V13.txt


Total Effect (Model D)
Run:
scripts/model_d_regression_main_effect.py
Output:
Model_D_Total_Effect_Results.txt


Heterogeneity Models (Models E, F)
Run:
scripts/hospital_closure_integration.py

Results printed to terminal.




Visualization and Tables


Summary Statistics
Run:
summary_stats_table_code.py

Output:
Summary_stats_Table_1.csv


Geographic and Trend Graphs
Run:
scripts/map_produces_graphs.py

Outputs:
debt_trend_overall.pdf
debt_race_equity.pdf
debt_geo_interaction.pdf
unemployment_resilence.pdf

futher graphs/visualizations

Run: 
scripts/other_graphs.py

Outputs:
Unemployment_debt_shock.png
debt_correltation_heatmap.png
debt_race_interaction.png


Correlation and Infrastructure Analysis
Run:
scripts/initial_graphs.py

Outputs:
debt_trend_geo.pdf
debt_geo_interaction.pdf
hosp_vs_debt_correlation.pdf

Event Study
Run:
Event_study_plot.py

Outputs:
event_study_v13.pdf
event_study_v13.png


Hospital Closure Analysis
Run:
scripts/hosptial_closure_intergration.py

Outputs:
hospital_closure_heterogeneity.pdf
hospital_closure_heterogeneity.png
Main Results: The Rural Friction Gap (TWFE)


Table 2: Estimated Policy Impact (2012–2023)
N = 35,868

Variable	Coefficient (β)	Std. Error	P-Value	Significance
Expansion × Rural	0.0073	0.0018	<0.0001	p < 0.001
Uninsured Rate	0.0029	0.0003	<0.0001	p < 0.001
Unemployment Rate	0.0016	0.0003	<0.0001	p < 0.001
Median Income	1.36e-06	1.16e-07	<0.0001	p < 0.001
Interpretation

The positive and significant coefficient on the Rural Interaction term indicates a Discovery Effect.

After controlling for the debt-reducing effects of insurance expansion, Medicaid expansion leads to a significant formalization of medical debt in rural areas due to the sudden utilization of an already strained healthcare infrastructure.

Notes on Replication

Missing Data

This project uses listwise deletion for counties with missing ACS covariates to maintain a balanced panel.

Attrition

The cleaning process resulted in a 95.1% data retention rate from the initial merged dataset.

File Paths

Ensure the directory structure follows the Repository Structure described above so scripts execute correctly.

