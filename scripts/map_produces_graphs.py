import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 1. Load your Master Dataset
df = pd.read_csv('FINAL_DATASET_V13_MASTER.csv')

# 2. CREATE MISSING COLUMNS
df['state'] = df['full_name'].str.split(',').str[-1].str.strip()
df['poc_category'] = np.where(df['pct_poc'] > df['pct_poc'].median(), 'High % POC', 'Low % POC')

# Helper to map 0/1 to clear text for legends
df['Expansion Status'] = df['medicaid_expansion'].map({0: 'Non-Expansion', 1: 'Expansion'})

# 3. SET THE THEME FOR POSTERS
sns.set_theme(style="whitegrid", context="talk")
plt.rcParams.update({'font.family': 'serif'})

# --- GRAPH 1: Overall Debt Trends ---
plt.figure(figsize=(12, 7))
sns.lineplot(data=df, x='year', y='share_debt_all', hue='Expansion Status',
             palette=['#A52A2A', '#00693e'], marker='o', linewidth=3, markersize=10)

plt.axvline(x=2014, color='black', linestyle='--', linewidth=2, label='Policy Implementation')

plt.title('Medical Debt Trends: Expansion vs. Non-Expansion States', fontsize=26, pad=20, fontweight='bold')
plt.ylabel('Share of Population with Medical Debt', fontsize=20)
plt.xlabel('Year', fontsize=20)
plt.legend(title='Medicaid Status', fontsize=16, title_fontsize=18)

plt.savefig('debt_trend_overall.pdf', format='pdf', bbox_inches='tight')
print("Saved: debt_trend_overall.pdf")

# --- GRAPH 2: Racial Equity Interaction ---
plt.figure(figsize=(12, 7))
# Combining the categories for a cleaner legend
sns.lineplot(data=df, x='year', y='share_debt_all', hue='poc_category',
             style='Expansion Status', palette='Dark2', linewidth=3)

plt.title('Medical Debt by Racial Diversity & Expansion Status', fontsize=24, pad=20, fontweight='bold')
plt.ylabel('Share of Population with Medical Debt', fontsize=20)
plt.xlabel('Year', fontsize=20)
plt.legend(fontsize=14, title_fontsize=16, loc='upper right', bbox_to_anchor=(1.3, 1))

plt.savefig('debt_race_equity.pdf', format='pdf', bbox_inches='tight')
print("Saved: debt_race_equity.pdf")

# --- GRAPH 3: Geographic Disparity (The Interaction) ---
g = sns.FacetGrid(df, col="geo_type", col_order=['Urban', 'Suburban', 'Rural'],
                  height=6, aspect=0.9, hue='Expansion Status', palette=['#A52A2A', '#00693e'])
g.map_dataframe(sns.lineplot, x="year", y="share_debt_all", marker='o', linewidth=2)

g.set_axis_labels("Year", "Share of Medical Debt", fontsize=18)
g.set_titles("{col_name} Counties", size=22, fontweight='bold')
g.add_legend(title="Medicaid Status", fontsize=16, title_fontsize=18)

plt.subplots_adjust(top=0.8)
g.fig.suptitle('Expansion Impact Across Geography', fontsize=28, fontweight='bold')

plt.savefig('debt_geo_interaction.pdf', format='pdf', bbox_inches='tight')
print("Saved: debt_geo_interaction.pdf")

# --- GRAPH 4: Unemployment Shock (Resilience) ---
plt.figure(figsize=(12, 7))
# Use meaningful labels for regression plots
sample_non = df[df['medicaid_expansion']==0].sample(min(1000, len(df)))
sample_exp = df[df['medicaid_expansion']==1].sample(min(1000, len(df)))

sns.regplot(data=sample_non, x='unemployment_rate', y='share_debt_all',
            label='Non-Expansion States', color='#A52A2A', scatter_kws={'alpha':0.2, 's':40})
sns.regplot(data=sample_exp, x='unemployment_rate', y='share_debt_all',
            label='Expansion States', color='#00693e', scatter_kws={'alpha':0.2, 's':40})

plt.title('Economic Resilience: Unemployment vs. Medical Debt', fontsize=26, pad=20, fontweight='bold')
plt.xlabel('Unemployment Rate (%)', fontsize=20)
plt.ylabel('Share of Medical Debt', fontsize=20)
plt.legend(fontsize=16)

plt.savefig('unemployment_resilience.pdf', format='pdf', bbox_inches='tight')
print("Saved: unemployment_resilience.pdf")

plt.show()