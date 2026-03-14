import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load the master dataset containing clinical mechanism data
df = pd.read_csv('/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/data/processed/FINAL_DATASET_V13_MASTER.csv')

# Use whitegrid theme for clear readability in the final report
sns.set_theme(style="whitegrid")

# Initialize bar plot to compare hospitalization rates across the rural-urban continuum
plt.figure(figsize=(10, 6))
plot = sns.barplot(
    data=df,
    x='geo_type',
    y='preventable_hosp_rate',
    palette='viridis',
    order=['Urban', 'Suburban', 'Rural']  # Ordering logically by density
)

# Labeling for clinical failure mechanism analysis
plt.title('Preventable Hospitalization Rates by Geographic Type (2012-2020)', fontsize=14)
plt.xlabel('Geographic Classification', fontsize=12)
plt.ylabel('Rate per 100,000 Medicare Enrollees', fontsize=12)

# Export high-resolution figure for the LaTeX document
plt.tight_layout()
plt.savefig('/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/figures/hosp_rate_by_geography.png', dpi=300)
plt.show()

print("Graph saved as 'hosp_rate_by_geography.png'")