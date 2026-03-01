import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Load the dataset
# Replace with your actual filename, e.g., 'FINAL_DATASET_V12_MASTER.csv'
df = pd.read_csv('FINAL_DATASET_V13_MASTER.csv')

# 2. Select the "Particular Years" for comparison
# 2013 is the Pre-Expansion baseline; 2019 is a stable Post-Expansion year
years_to_compare = [2013, 2019]
df_filtered = df[df['year'].isin(years_to_compare)].copy()

# 3. Clean Medicaid Expansion labels for the legend
df_filtered['Status'] = df_filtered['medicaid_expansion'].map({1: 'Expansion', 0: 'Non-Expansion'})

# 4. Create the Plot
sns.set_theme(style="whitegrid")
g = sns.catplot(
    data=df_filtered,
    x='year',
    y='preventable_hosp_rate',
    hue='Status',
    col='geo_type',
    kind='point',
    palette={'Expansion': '#E69F00', 'Non-Expansion': '#56B4E9'}, # Colorblind-friendly
    capsize=.1,
    join=True,
    col_order=['Urban', 'Suburban', 'Rural']
)

# 5. Styling and Labels
g.set_axis_labels("Comparison Year", "Preventable Hosp. Rate (per 100k)")
g.set_titles("{col_name} Counties")
plt.subplots_adjust(top=0.85)
g.fig.suptitle('Clinical Impact: Change in Preventable Hospitalizations (2013 vs 2019)', fontsize=16)

# 6. Save the visualization
plt.savefig('hosp_effect_by_year.png', dpi=300)
plt.show()

print("Graph for 2013 vs 2019 saved as 'hosp_effect_by_year.png'")