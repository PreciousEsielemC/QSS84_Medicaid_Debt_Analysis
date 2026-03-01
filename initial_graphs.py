import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load your Master Dataset
# If you are using the CSV file:
df = pd.read_csv('FINAL_DATASET_V13_MASTER.csv')

# --- GRAPH 1: Overall Debt Trends (Expansion vs. Non-Expansion) ---
plt.figure(figsize=(12, 6))
sns.lineplot(data=df, x='year', y='share_debt_all', hue='medicaid_expansion', marker='o')

# Adding a vertical line for the 2014 policy implementation
plt.axvline(x=2014, color='red', linestyle='--', label='ACA Expansion Start')

plt.title('Medical Debt Trends: Expansion vs. Non-Expansion States (2012-2023)')
plt.ylabel('Share of Population with Medical Debt')
plt.xlabel('Year')
plt.legend(title='Medicaid Expansion', labels=['Non-Expansion (0)', 'Expansion (1)'])
plt.grid(True, alpha=0.3)
plt.savefig('debt_trend_expansion.png')
print("Saved: debt_trend_expansion.png")


# --- GRAPH 2: Geographic Trends (Urban vs. Suburban vs. Rural) ---
plt.figure(figsize=(12, 6))
sns.lineplot(data=df, x='year', y='share_debt_all', hue='geo_type',
             hue_order=['Urban', 'Suburban', 'Rural'], marker='s')

plt.title('Medical Debt Levels by Geographic County Type')
plt.ylabel('Share of Population with Medical Debt')
plt.xlabel('Year')
plt.grid(True, alpha=0.3)
plt.savefig('debt_trend_geo.png')
print("Saved: debt_trend_geo.png")


# --- GRAPH 3: The Interaction (Expansion Impact per Geo Type) ---
# This creates a "FacetGrid" (side-by-side plots)
g = sns.FacetGrid(df, col="geo_type", col_order=['Urban', 'Suburban', 'Rural'],
                  height=5, aspect=0.8)
g.map_dataframe(sns.lineplot, x="year", y="share_debt_all", hue="medicaid_expansion", marker='o')

g.set_axis_labels("Year", "Share of Medical Debt")
g.add_legend(title="Expansion Status")
plt.subplots_adjust(top=0.8)
g.fig.suptitle('Expansion Impact: Urban vs. Suburban vs. Rural Comparison')
plt.savefig('debt_interaction_geo.png')
print("Saved: debt_interaction_geo.png")


# --- GRAPH 4: Mechanism Check (Hospitalization vs. Debt) ---
# Filter for years 2012-2020 where we have hospitalization data
df_hosp = df[df['year'] <= 2020].dropna(subset=['preventable_hosp_rate', 'share_debt_all'])

plt.figure(figsize=(10, 6))
# Using a sample of 2000 points so the plot isn't too crowded
sns.scatterplot(data=df_hosp.sample(2000), x='preventable_hosp_rate', y='share_debt_all', alpha=0.4)
# Add a trend line
sns.regplot(data=df_hosp.sample(2000), x='preventable_hosp_rate', y='share_debt_all',
            scatter=False, color='red')

plt.title('Mechanism Check: Preventable Hospitalizations vs. Medical Debt')
plt.xlabel('Preventable Hospital Stays (per 100,000 residents)')
plt.ylabel('Share of Medical Debt')
plt.savefig('hosp_vs_debt_correlation.png')
print("Saved: hosp_vs_debt_correlation.png")

plt.show() # This will pop the graphs up on your screen in PyCharm