import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# -------------------------------------------------------------
# VISUALIZATION SCRIPT: MEDICAID EXPANSION & MEDICAL DEBT
# -------------------------------------------------------------
# This script generates the core figures used in the empirical
# analysis of how Medicaid expansion relates to medical debt
# across U.S. counties.
#
# The figures produced illustrate:
#   1. Overall medical debt trends in expansion vs. non-expansion states
#   2. Racial equity differences in medical debt trajectories
#   3. Geographic variation in expansion effects (urban/suburban/rural)
#   4. Economic resilience: how unemployment shocks relate to debt
#
# These figures are formatted for inclusion in the final paper
# or poster presentation.
# -------------------------------------------------------------

# -------------------------------------------------------------
# STEP 1: LOAD MASTER DATASET
# -------------------------------------------------------------
# Import the cleaned and merged county-year dataset used in
# the main analysis. This version excludes hospitalization
# variables to simplify visualization.
df = pd.read_csv('/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/data/processed/FINAL_DATASET_V13_NO_HOSP.csv')

# -------------------------------------------------------------
# STEP 2: CREATE ADDITIONAL ANALYSIS VARIABLES
# -------------------------------------------------------------

# Extract state abbreviation/name from the county identifier
# stored in the "full_name" column (format: County, State)
df['state'] = df['full_name'].str.split(',').str[-1].str.strip()

# Create a binary racial diversity indicator based on whether
# the county's percent population-of-color is above or below
# the national median. This allows us to compare medical debt
# trends in more diverse vs. less diverse counties.
df['poc_category'] = np.where(
    df['pct_poc'] > df['pct_poc'].median(),
    'High % POC',
    'Low % POC'
)

# Convert the Medicaid expansion indicator (0/1) into readable
# labels for figure legends and interpretation.
df['Expansion Status'] = df['medicaid_expansion'].map({
    0: 'Non-Expansion',
    1: 'Expansion'
})

# -------------------------------------------------------------
# STEP 3: SET VISUAL STYLE FOR FIGURES
# -------------------------------------------------------------
# Apply a clean academic plotting theme suitable for research
# presentations and posters.
sns.set_theme(style="whitegrid", context="talk")

# Use serif fonts to match typical academic publication style
plt.rcParams.update({'font.family': 'serif'})

# -------------------------------------------------------------
# GRAPH 1: OVERALL MEDICAL DEBT TRENDS
# -------------------------------------------------------------
# This figure compares average medical debt levels over time
# between counties in Medicaid expansion states and those in
# non-expansion states.
#
# The vertical line marks the implementation of Medicaid
# expansion under the Affordable Care Act in 2014.

plt.figure(figsize=(12, 7))

sns.lineplot(
    data=df,
    x='year',
    y='share_debt_all',
    hue='Expansion Status',
    palette=['#A52A2A', '#00693e'],
    marker='o',
    linewidth=3,
    markersize=10
)

# Reference line indicating policy implementation year
plt.axvline(
    x=2014,
    color='black',
    linestyle='--',
    linewidth=2,
    label='Policy Implementation'
)

plt.title('Medical Debt Trends: Expansion vs. Non-Expansion States', fontsize=26, pad=20, fontweight='bold')
plt.ylabel('Share of Population with Medical Debt', fontsize=20)
plt.xlabel('Year', fontsize=20)
plt.legend(title='Medicaid Status', fontsize=16, title_fontsize=18)

# Save figure as a high-resolution PDF for reporting
plt.savefig(
    '/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/figures/debt_trend_overall.pdf',
    format='pdf',
    bbox_inches='tight'
)

print("Saved: debt_trend_overall.pdf")

# -------------------------------------------------------------
# GRAPH 2: RACIAL EQUITY INTERACTION
# -------------------------------------------------------------
# This visualization examines whether the relationship between
# Medicaid expansion and medical debt differs across counties
# with higher vs. lower racial diversity.
#
# Line color represents racial composition categories, while
# line style represents expansion status.

plt.figure(figsize=(12, 7))

sns.lineplot(
    data=df,
    x='year',
    y='share_debt_all',
    hue='poc_category',
    style='Expansion Status',
    palette='Dark2',
    linewidth=3
)

plt.title('Medical Debt by Racial Diversity & Expansion Status', fontsize=24, pad=20, fontweight='bold')
plt.ylabel('Share of Population with Medical Debt', fontsize=20)
plt.xlabel('Year', fontsize=20)

# Place legend slightly outside the figure to avoid crowding
plt.legend(fontsize=14, title_fontsize=16, loc='upper right', bbox_to_anchor=(1.3, 1))

# Save racial equity figure
plt.savefig(
    '/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/figures/debt_race_equity.pdf',
    format='pdf',
    bbox_inches='tight'
)

print("Saved: debt_race_equity.pdf")

# -------------------------------------------------------------
# GRAPH 3: GEOGRAPHIC INTERACTION EFFECT
# -------------------------------------------------------------
# This figure explores whether the relationship between
# Medicaid expansion and medical debt differs by geographic
# context (Urban, Suburban, Rural counties).
#
# Faceting allows each geographic category to be viewed in
# separate panels for easier comparison.

g = sns.FacetGrid(
    df,
    col="geo_type",
    col_order=['Urban', 'Suburban', 'Rural'],
    height=6,
    aspect=0.9,
    hue='Expansion Status',
    palette=['#A52A2A', '#00693e']
)

# Plot time trends within each geographic panel
g.map_dataframe(
    sns.lineplot,
    x="year",
    y="share_debt_all",
    marker='o',
    linewidth=2
)

# Set axis labels and panel titles
g.set_axis_labels("Year", "Share of Medical Debt", fontsize=18)
g.set_titles("{col_name} Counties", size=22, fontweight='bold')

# Add legend explaining expansion status
g.add_legend(title="Medicaid Status", fontsize=16, title_fontsize=18)

plt.subplots_adjust(top=0.8)

g.fig.suptitle('Expansion Impact Across Geography', fontsize=28, fontweight='bold')

# Save geographic interaction figure
plt.savefig(
    '/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/figures/debt_geo_interaction.pdf',
    format='pdf',
    bbox_inches='tight'
)

print("Saved: debt_geo_interaction.pdf")

# -------------------------------------------------------------
# GRAPH 4: ECONOMIC RESILIENCE (UNEMPLOYMENT SHOCK)
# -------------------------------------------------------------
# This figure investigates whether counties in Medicaid
# expansion states are more resilient to economic shocks.
#
# Specifically, it plots the relationship between unemployment
# rates and medical debt levels in expansion vs. non-expansion
# states.

plt.figure(figsize=(12, 7))

# Create balanced random samples to reduce visual clutter
sample_non = df[df['medicaid_expansion'] == 0].sample(min(1000, len(df)))
sample_exp = df[df['medicaid_expansion'] == 1].sample(min(1000, len(df)))

# Regression relationship for non-expansion states
sns.regplot(
    data=sample_non,
    x='unemployment_rate',
    y='share_debt_all',
    label='Non-Expansion States',
    color='#A52A2A',
    scatter_kws={'alpha': 0.2, 's': 40}
)

# Regression relationship for expansion states
sns.regplot(
    data=sample_exp,
    x='unemployment_rate',
    y='share_debt_all',
    label='Expansion States',
    color='#00693e',
    scatter_kws={'alpha': 0.2, 's': 40}
)

plt.title('Economic Resilience: Unemployment vs. Medical Debt', fontsize=26, pad=20, fontweight='bold')
plt.xlabel('Unemployment Rate (%)', fontsize=20)
plt.ylabel('Share of Medical Debt', fontsize=20)

plt.legend(fontsize=16)

# Save resilience analysis figure
plt.savefig(
    '/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/figures/unemployment_resilience.pdf',
    format='pdf',
    bbox_inches='tight'
)

print("Saved: unemployment_resilience.pdf")

# Display all generated figures
plt.show()