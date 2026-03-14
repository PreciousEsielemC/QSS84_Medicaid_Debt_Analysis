import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Loading the V13 master panel to look at the clinical mechanism distribution
df = pd.read_csv('/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/data/processed/FINAL_DATASET_V13_MASTER.csv')

# Using whitegrid for a clean, professional look in the final report
sns.set_theme(style="whitegrid")

# Generating a boxplot to compare the spread of hospital rates across different geographies
# This helps visualize the higher baseline 'friction' in rural areas
plt.figure(figsize=(10, 6))
plot = sns.boxplot(
    data=df,
    x='geo_type',
    y='preventable_hosp_rate',
    palette='viridis',
    order=['Urban', 'Suburban', 'Rural']  # Keeping the density gradient consistent
)

# Labeling axes for the clinical infrastructure analysis section
plt.title('Preventable Hospitalization Rates by Geographic Type (2012-2023)', fontsize=14)
plt.xlabel('Geographic Classification', fontsize=12)
plt.ylabel('Rate per 100,000 Medicare Enrollees', fontsize=12)

# Save the figure as a high-res PNG for the methodology appendix
plt.tight_layout()
plt.savefig('/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/figures/hosp_rate_by_geography.png', dpi=300)
plt.show()

print("Distribution graph saved: hosp_rate_by_geography.png")