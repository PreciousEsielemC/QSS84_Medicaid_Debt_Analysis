import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# -------------------------------------------------------------
# STEP 1: LOAD MASTER DATASET
# -------------------------------------------------------------
# Import the cleaned county-year dataset used for the analysis.
# This dataset contains socioeconomic, demographic, and healthcare
# variables used to examine patterns in medical debt across counties.
df = pd.read_csv('/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/data/processed/FINAL_DATASET_V13_MASTER.csv')


# -------------------------------------------------------------
# GRAPH 1: RACIAL COMPOSITION & MEDICAID EXPANSION
# -------------------------------------------------------------
# This figure examines whether medical debt trends differ across
# counties with different racial compositions and whether Medicaid
# expansion moderates those differences.
#
# Counties are divided into two groups based on the median share
# of residents who are people of color (POC):
#   • High % POC counties
#   • Low % POC counties
#
# The plot shows medical debt trends over time, while also distinguishing
# between Medicaid expansion and non-expansion states. This allows
# visual inspection of whether expansion policies coincide with
# different debt trajectories across racial composition categories.

df['poc_category'] = np.where(df['pct_poc'] > df['pct_poc'].median(), 'High % POC', 'Low % POC')

plt.figure(figsize=(12, 6))

# The "style" parameter differentiates expansion vs non-expansion states
# using dashed and solid lines, allowing both racial composition and
# policy status to be displayed simultaneously.
sns.lineplot(
    data=df,
    x='year',
    y='share_debt_all',
    hue='poc_category',
    style='medicaid_expansion',
    markers=True,
    dashes=True
)

# Add a vertical reference line marking the beginning of major ACA
# Medicaid expansions in 2014.
plt.axvline(x=2014, color='red', linestyle='--', label='ACA Expansion Start')

plt.title('Medical Debt Trends: Impact of Medicaid Expansion on Racial Equity')
plt.ylabel('Share of Population with Medical Debt')
plt.xlabel('Year')

# Place legend outside the plot for readability
plt.legend(title='Category & Expansion Status', bbox_to_anchor=(1.05, 1), loc='upper left')

plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig('/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/figures/debt_race_interaction.png')
print("Saved: debt_race_interaction.png")


# -------------------------------------------------------------
# GRAPH 2: CORRELATION HEATMAP OF DEBT DRIVERS
# -------------------------------------------------------------
# This figure visualizes pairwise correlations between key variables
# in the dataset. It provides a descriptive overview of how economic,
# demographic, and healthcare factors relate to medical debt.
#
# The goal is exploratory rather than causal: identifying which
# variables tend to move together with medical debt across counties.

numeric_cols = [
    'share_debt_all', 'median_income', 'unemployment_rate',
    'median_age', 'pct_65_plus', 'uninsured_rate',
    'pct_poc', 'preventable_hosp_rate'
]

# Compute the Pearson correlation matrix for selected variables
corr_matrix = df[numeric_cols].corr()

plt.figure(figsize=(10, 8))

# Heatmap colors represent the strength and direction of correlations.
# Values closer to +1 or -1 indicate stronger relationships.
sns.heatmap(
    corr_matrix,
    annot=True,
    cmap='coolwarm',
    fmt=".2f",
    linewidths=0.5
)

plt.title('Correlation Heatmap: What Drives Medical Debt?')
plt.tight_layout()

plt.savefig('/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/figures/debt_correlation_heatmap.png')
print("Saved: debt_correlation_heatmap.png")


# -------------------------------------------------------------
# GRAPH 3: UNEMPLOYMENT SHOCK & FINANCIAL RESILIENCE
# -------------------------------------------------------------
# This figure explores the relationship between unemployment and
# medical debt. Economic shocks—such as job loss—may reduce access
# to employer-sponsored insurance and increase financial strain,
# potentially leading to higher medical debt.
#
# The scatter plot shows the relationship between county unemployment
# rates and the share of residents with medical debt. Separate
# regression lines are estimated for expansion and non-expansion
# states to examine whether Medicaid expansion may buffer counties
# from unemployment-related debt increases.

plt.figure(figsize=(10, 6))

# Use a random sample to reduce computational load while preserving
# the overall pattern in the data.
plot = sns.lmplot(
    data=df.sample(3000),
    x='unemployment_rate',
    y='share_debt_all',
    hue='medicaid_expansion',
    aspect=1.5,
    scatter_kws={'alpha':0.2},
    palette='viridis'
)

# Add descriptive title and axis labels
new_title = 'The Unemployment-to-Debt Pipeline'
plot.fig.suptitle(new_title, y=1.05)
plot.set_axis_labels("Unemployment Rate (%)", "Share of Medical Debt")

# Rename legend for clarity
plot._legend.set_title("Medicaid Expansion")

plt.savefig('/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/figures/unemployment_debt_shock.png')
print("Saved: unemployment_debt_shock.png")


# -------------------------------------------------------------
# FINAL STEP: DISPLAY FIGURES
# -------------------------------------------------------------
# If running the script interactively (e.g., in an IDE), this command
# renders all generated plots in a viewing window.
plt.show()