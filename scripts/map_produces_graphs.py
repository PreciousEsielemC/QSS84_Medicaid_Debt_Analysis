import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 1. Load your Master Dataset
df = pd.read_csv('FINAL_DATASET_V13_MASTER.csv')

# 2. CREATE MISSING COLUMNS (The Fix)
# Extract state from "County, State"
df['state'] = df['full_name'].str.split(',').str[-1].str.strip()

# Create POC category for the equity graph
df['poc_category'] = np.where(df['pct_poc'] > df['pct_poc'].median(), 'High % POC', 'Low % POC')

# 3. SET THE THEME
sns.set_theme(style="whitegrid")

# --- GRAPH 1: Overall Debt Trends ---
plt.figure(figsize=(10, 6))
sns.lineplot(data=df, x='year', y='share_debt_all', hue='medicaid_expansion', marker='o')
plt.axvline(x=2014, color='red', linestyle='--', label='Expansion Start')
plt.title('Medical Debt Trends (2012-2023)')
plt.legend(title='Medicaid Expansion', labels=['Non-Expansion', 'Expansion'])
plt.savefig('debt_trend_overall.png')
print("Saved: debt_trend_overall.png")

# --- GRAPH 2: Racial Equity Interaction ---
plt.figure(figsize=(10, 6))
sns.lineplot(data=df, x='year', y='share_debt_all', hue='poc_category', style='medicaid_expansion')
plt.title('Medical Debt by Racial Diversity & Expansion Status')
plt.savefig('debt_race_equity.png')
print("Saved: debt_race_equity.png")

# --- GRAPH 3: Geographic Disparity (The Interaction) ---
g = sns.FacetGrid(df, col="geo_type", col_order=['Urban', 'Suburban', 'Rural'], height=5, aspect=0.8)
g.map_dataframe(sns.lineplot, x="year", y="share_debt_all", hue="medicaid_expansion", marker='o')
g.add_legend(title="Expansion")
plt.subplots_adjust(top=0.8)
g.fig.suptitle('Expansion Impact Across Geography')
plt.savefig('debt_geo_interaction.png')
print("Saved: debt_geo_interaction.png")

# --- GRAPH 4: Unemployment Shock (Resilience) ---
plt.figure(figsize=(10, 6))
sns.regplot(data=df[df['medicaid_expansion']==0].sample(1000), x='unemployment_rate', y='share_debt_all',
            label='Non-Expansion', color='blue', scatter_kws={'alpha':0.2})
sns.regplot(data=df[df['medicaid_expansion']==1].sample(1000), x='unemployment_rate', y='share_debt_all',
            label='Expansion', color='orange', scatter_kws={'alpha':0.2})
plt.title('Economic Resilience: Unemployment vs Medical Debt')
plt.legend()
plt.savefig('unemployment_resilience.png')
print("Saved: unemployment_resilience.png")

plt.show()
