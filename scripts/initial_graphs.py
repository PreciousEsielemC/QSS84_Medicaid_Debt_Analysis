import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# -------------------------------------------------------------
# VISUALIZATION SCRIPT FOR FINAL PROJECT FIGURES
# -------------------------------------------------------------
# This script generates three publication-quality figures used
# in the final analysis of Medicaid expansion and medical debt.
#
# The figures illustrate:
#   1. Baseline debt trends by geography (Urban vs. Rural)
#   2. The expansion interaction (Expansion vs. Non-Expansion)
#   3. A mechanism check linking preventable hospitalizations
#      to medical debt levels.
#
# -------------------------------------------------------------

# Set a clean publication-style theme suitable for academic figures
sns.set_theme(style="whitegrid", context="talk")

# Use a serif font to match common academic presentation styles
plt.rcParams.update({'font.family': 'serif'})

# -------------------------------------------------------------
# STEP 1: LOAD MASTER DATASET
# -------------------------------------------------------------
# Import the processed county-year dataset containing medical
# debt outcomes, Medicaid expansion status, geographic
# classification, and control variables.
df = pd.read_csv('/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/data/processed/FINAL_DATASET_V13_MASTER.csv')

# -------------------------------------------------------------
# STEP 2: FILTER GEOGRAPHIC GROUPS
# -------------------------------------------------------------
# Restrict the analysis to Urban and Rural counties only.
# Suburban counties are removed to simplify comparisons and
# emphasize the contrast between highly urban and highly rural
# areas.
df_filtered = df[df['geo_type'].isin(['Urban', 'Rural'])].copy()

# Helper function to convert the numeric Medicaid expansion
# indicator into readable labels for figure legends.
def fix_labels(df):
    df['Medicaid Status'] = df['medicaid_expansion'].map({0: 'Non-Expansion', 1: 'Expansion'})
    return df

df_filtered = fix_labels(df_filtered)

# -------------------------------------------------------------
# GRAPH 1: BASELINE DEBT TRENDS BY GEOGRAPHY
# -------------------------------------------------------------
# This figure shows the overall trend in the share of residents
# with medical debt for Urban and Rural counties across time.
# It provides a descriptive baseline illustrating the persistent
# rural-urban gap in medical debt before and after expansion.

plt.figure(figsize=(14, 8))

sns.lineplot(
    data=df_filtered,
    x='year',
    y='share_debt_all',
    hue='geo_type',
    palette=['#4682B4', '#A52A2A'],
    linewidth=4,
    marker='s',
    markersize=12
)

plt.title('Medical Debt Baseline: Urban vs. Rural Counties', fontsize=26, pad=20, fontweight='bold')
plt.ylabel('Share of Population with Medical Debt', fontsize=22)
plt.xlabel('Year', fontsize=22)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.legend(title='Geography', fontsize=18, title_fontsize=20)

# Save figure as a high-resolution PDF for inclusion in reports
plt.savefig(
    '/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/figures/debt_trend_geo.pdf',
    format='pdf',
    bbox_inches='tight'
)

print("Saved: debt_trend_geo.pdf")

# -------------------------------------------------------------
# GRAPH 2: EXPANSION INTERACTION (URBAN VS RURAL)
# -------------------------------------------------------------
# This figure visualizes the core policy interaction by plotting
# trends separately for Expansion and Non-Expansion states within
# Urban and Rural counties.
#
# Faceting allows direct comparison of how the expansion effect
# differs across geographic contexts.

g = sns.FacetGrid(
    df_filtered,
    col="geo_type",
    col_order=['Urban', 'Rural'],
    height=7,
    aspect=0.9,
    hue="Medicaid Status",
    palette=['#A52A2A', '#00693e']
)

# Plot time-series trends within each geographic panel
g.map_dataframe(
    sns.lineplot,
    x="year",
    y="share_debt_all",
    linewidth=4,
    marker='o',
    markersize=10
)

# Format panel titles and axis labels
g.set_titles("{col_name} Counties", size=24, fontweight='bold')
g.set_axis_labels("Year", "Share of Medical Debt", fontsize=22)

# Add a vertical reference line marking the start of Medicaid expansion (2014)
for ax in g.axes.flat:
    ax.axvline(x=2014, color='black', linestyle='--', alpha=0.7)
    ax.tick_params(labelsize=18)

plt.subplots_adjust(top=0.82, wspace=0.2)

g.fig.suptitle('Expansion Impact: Urban vs. Rural Divergence', fontsize=28, fontweight='bold')

# Add legend explaining expansion status
g.add_legend(title="Medicaid Status", fontsize=18, title_fontsize=20)

# Save the interaction figure
plt.savefig(
    '/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/figures/debt_geo_interaction.pdf',
    format='pdf',
    bbox_inches='tight'
)

print("Saved: debt_geo_interaction.pdf")

# -------------------------------------------------------------
# GRAPH 3: MECHANISM CHECK
# -------------------------------------------------------------
# This scatterplot evaluates the proposed mechanism linking
# health system access to medical debt.
#
# Specifically, it examines whether counties with higher
# preventable hospitalization rates also tend to have higher
# levels of medical debt.

# Restrict analysis to years with reliable hospitalization data
df_hosp = df_filtered[df_filtered['year'] <= 2020].dropna(
    subset=['preventable_hosp_rate', 'share_debt_all']
)

# Draw a random sample to reduce overplotting in the scatterplot
sample_data = df_hosp.sample(min(2500, len(df_hosp)))

plt.figure(figsize=(12, 8))

# Plot sampled county-year observations
sns.scatterplot(
    data=sample_data,
    x='preventable_hosp_rate',
    y='share_debt_all',
    alpha=0.4,
    color='#4682B4',
    s=100
)

# Add regression line summarizing the correlation pattern
sns.regplot(
    data=sample_data,
    x='preventable_hosp_rate',
    y='share_debt_all',
    scatter=False,
    color='#A52A2A',
    line_kws={"linewidth":5}
)

plt.title('Mechanism: Preventable Hospitalizations vs. Medical Debt', fontsize=26, pad=20, fontweight='bold')
plt.xlabel('Preventable Hospital Stays (per 100,000 residents)', fontsize=22)
plt.ylabel('Share of Population with Medical Debt', fontsize=22)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)

# Save the mechanism figure
plt.savefig(
    '/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/figures/hosp_vs_debt_correlation.pdf',
    format='pdf',
    bbox_inches='tight'
)

print("Saved: hosp_vs_debt_correlation.pdf")

# Display all figures in the interactive window
plt.show()