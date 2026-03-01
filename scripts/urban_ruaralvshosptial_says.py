import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Load your master dataset
# Ensure your CSV filename matches exactly
df = pd.read_csv('FINAL_DATASET_V13_MASTER.csv')

# 2. Set the aesthetic style
sns.set_theme(style="whitegrid")

# 3. Create the Visualization
plt.figure(figsize=(10, 6))
plot = sns.barplot(
    data=df,
    x='geo_type',
    y='preventable_hosp_rate',
    palette='viridis',
    order=['Urban', 'Suburban', 'Rural']  # Keeps the x-axis organized
)

# 4. Add Labels and Title
plt.title('Preventable Hospitalization Rates by Geographic Type (2012-2023)', fontsize=14)
plt.xlabel('Geographic Classification', fontsize=12)
plt.ylabel('Rate per 100,000 Medicare Enrollees', fontsize=12)

# 5. Save and Show
plt.tight_layout()
plt.savefig('hosp_rate_by_geography.png', dpi=300)
plt.show()

print("Graph saved as 'hosp_rate_by_geography.png'")
