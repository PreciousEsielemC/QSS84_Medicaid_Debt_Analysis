import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Load the dataset
# Read in the main dataset that contains the hospital utilization variables.
# Update the path if the file location changes.
df = pd.read_csv('/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/data/processed/FINAL_DATASET_V13_MASTER.csv')

# 2. Select the years used for the comparison
# 2013 is used as the pre-expansion reference point.
# 2019 is chosen as a post-expansion year after the policy had time to take effect.
years_to_compare = [2013, 2019]
df_filtered = df[df['year'].isin(years_to_compare)].copy()

# 3. Create cleaner labels for the expansion variable
# Convert the 0/1 expansion indicator into readable text for the plot legend.
df_filtered['Status'] = df_filtered['medicaid_expansion'].map({1: 'Expansion', 0: 'Non-Expansion'})

# 4. Build the plot
# Use seaborn's catplot with point estimates so we can compare expansion
# vs non-expansion states across county types.
sns.set_theme(style="whitegrid")
g = sns.catplot(
    data=df_filtered,
    x='year',
    y='preventable_hosp_rate',
    hue='Status',
    col='geo_type',
    kind='point',
    palette={'Expansion': '#E69F00', 'Non-Expansion': '#56B4E9'}, # colorblind-friendly palette
    capsize=.1,
    join=True,
    col_order=['Urban', 'Suburban', 'Rural']
)

# 5. Labels and formatting
# Add axis labels and titles to make the figure easier to read.
g.set_axis_labels("Comparison Year", "Preventable Hosp. Rate (per 100k)")
g.set_titles("{col_name} Counties")
plt.subplots_adjust(top=0.85)
g.fig.suptitle('Clinical Impact: Change in Preventable Hospitalizations (2013 vs 2019)', fontsize=16)

# 6. Save the figure
# Export the plot to the figures folder so it can be used in the report.
plt.savefig('/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/figures/hosp_effect_by_year.png', dpi=300)
plt.show()

print("Graph for 2013 vs 2019 saved as 'hosp_effect_by_year.png'")