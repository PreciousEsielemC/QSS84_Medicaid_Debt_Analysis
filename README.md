# QSS84_Medicaid_Debt_Analysis
Geographic Disparities in Medical Debt: The "Rural Friction" of Medicaid Expansion
Author: Precious Esielem

Institution: Dartmouth College, QSS 84

Date: March 2026
## Project OverviewThis research investigates how the impact of Medicaid Expansion on medical debt in collections varies across the urban-rural continuum. Specifically, it evaluates the "Rural Friction" hypothesis: the theory that geographic barriers and healthcare infrastructure deficits in rural areas diminish the financial protections typically provided by insurance expansion.### Key Finding Using a Two-Way Fixed Effects (TWFE) model on a panel of 26,581 observations, this study identifies a significant geographic divergence. While Medicaid Expansion successfully reduces debt in urban centers, it is associated with a 0.37 percentage point increase ($p=0.0105$) in medical debt in rural counties, a phenomenon largely mediated by high rates of preventable hospitalizations.
## Data Sources
Urban Institute: County-level medical debt in collections (2011–2023).

Kaiser Family Foundation (KFF): medicaid_expansion_kff.csv – Official state-level Medicaid expansion dates and status.

U.S. Census Bureau (ACS 5-Year): Socioeconomic controls including Median Household Income (S1903), Unemployment Rate (DP03), and Demographic Characteristics (DP05).

AHRQ / County Health Rankings: Preventable Hospitalization Rates used as the primary clinical mechanism.
## Econometric Specification
The primary causal analysis utilizes a Two-Way Fixed Effects (TWFE) Difference-in-Differences approach:$$share\_debt_{it} = \beta_1(Expansion_{it} \times Rural_i) + \gamma X_{it} + \alpha_i + \delta_t + \epsilon_{it}$$Where:$\alpha_i$ represents County Fixed Effects (controlling for time-invariant local factors).$\delta_t$ represents Year Fixed Effects (controlling for national economic shocks).$X_{it}$ is a vector of socioeconomic controls (Income, Unemployment, Uninsured Rate).Standard errors are clustered at the state level.
## How to Replicate
Follow these steps to reproduce the dataset and the final analysis:
### 1. Clone the Repository
git clone https://github.com/PreciousEsielemC/QSS84_Medicaid_Debt_Analysis.git
### 2. Environment Setup
Ensure you have downloaded all the data in the data/raw.
Ensure you have the following Python libraries installed:
pandas, numpy, statsmodels, linearmodels, matplotlib, seaborn, glob, re, and os.
### 3. Data Processing & Cleaning
Execute script for version 10 dataset: scripts/new_final_file_creates_v10.py and then for version 11 dataset run: scripts/creates_version 11_final.py and then the master cleaning script to produce the final analytical sample (V13): scripts/final_litewise_deletion_and_produces_final_dataset_v13.py


### 4. Generate Analysis & Figures
Run the following scripts to reproduce the findings and visualizations found in the report:

Regressions: scripts/regression_model_A_B.py, scripts/OLS_regression_model_A_B.py, and scripts/DiD_regression_rural_urban.py.

Visualizations: scripts/initial_graphs.py, scripts/other_graphs.py, scripts/map_produces_graphs.py, and scripts/Difference-in-Differences Point Plot.py.

Note: All regression summaries and tables are automatically exported to the tables/ directory, and visualizations are saved to the figures/ directory.

## Results at a Glance: The "Rural Friction" Effect
The following table summarizes the primary Two-Way Fixed Effects (TWFE) results from DiD_regression_rural_urban.py.

Variable,Coefficient (β),Std. Error,P-Value,Significance
Medicaid Expansion × Rural,0.0037,0.0014,0.0105,p<0.05
Unemployment Rate,0.0011,0.0005,0.0325,p<0.05
Median Income (per $10k),-0.0215,0.0003,0.0000,p<0.001
Uninsured Rate,0.0016,0.0003,0.0000,p<0.001

### Interpretation
The positive and significant coefficient on the Rural Interaction term ($0.0037$) indicates that rural counties experienced a relative increase in medical debt compared to urban counties following Medicaid expansion. This suggests that while insurance coverage expanded, the underlying "friction"—caused by higher preventable hospitalization rates ($p < 0.001$ in Model B)—offset the expected financial gains of the policy.
