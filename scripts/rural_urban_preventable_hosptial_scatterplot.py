import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set professional publication style for a clean look in the report
sns.set_theme(style="whitegrid", context="talk")
plt.rcParams.update({'font.family': 'serif'})

# Load the V13 master panel
df = pd.read_csv('/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/data/processed/FINAL_DATASET_V13_MASTER.csv')

# Focus specifically on the Urban vs Rural comparison for the mechanism analysis
df_filtered = df[df['geo_type'].isin(['Urban', 'Rural'])].copy()

# Filter for the pre-2021 window to avoid pandemic-related hospital data outliers
# Ensuring rows have both the outcome and the clinical mechanism variable
df_hosp = df_filtered[df_filtered['year'] <= 2020].dropna(subset=['preventable_hosp_rate', 'share_debt_all'])

# Initialize the scatter plot figure
plt.figure(figsize=(14, 9))

# Plotting the relationship between hospital stays and debt
# Different markers and colors help highlight the geographic clustering
sns.scatterplot(
    data=df_hosp,
    x='preventable_hosp_rate',
    y='share_debt_all',
    hue='geo_type',
    palette=['#4682B4', '#A52A2A'],  # Steel Blue for Urban, Brown-Red for Rural
    alpha=0.5,
    s=100,
    style='geo_type',
    markers={'Urban': 'o', 'Rural': 's'}
)

# Overlay a regression line to demonstrate the overall national correlation
# This visualizes the link between healthcare access and financial outcomes
sns.regplot(
    data=df_hosp,
    x='preventable_hosp_rate',
    y='share_debt_all',
    scatter=False,
    color='black',
    line_kws={"linewidth": 4, "linestyle": "--", "label": "National Trend Line"}
)

# Labeling and styling for professional presentation
plt.title('Mechanism: Preventable Hospitalizations vs. Medical Debt by Geography', fontsize=26, pad=20, fontweight='bold')
plt.xlabel('Preventable Hospital Stays (per 100,000 residents)', fontsize=22)
plt.ylabel('Share of Population with Medical Debt', fontsize=22)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)

# Legend positioning for clear data interpretation
plt.legend(title='County Type', fontsize=18, title_fontsize=20, loc='upper left')

# Exporting as a high-resolution PDF for the final paper
plt.savefig('/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/figures/hosp_vs_debt_geo_highlighted.pdf', format='pdf', bbox_inches='tight')
print("Saved: hosp_vs_debt_geo_highlighted.pdf")

plt.show()