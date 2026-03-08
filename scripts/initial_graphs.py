import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set professional publication style for the poster
sns.set_theme(style="whitegrid", context="talk")
plt.rcParams.update({'font.family': 'serif'})

# 1. Load Dataset
df = pd.read_csv('FINAL_DATASET_V13_MASTER.csv')

# 2. Filter for Urban and Rural only (Removing Suburban for cleaner comparison)
df_filtered = df[df['geo_type'].isin(['Urban', 'Rural'])].copy()

# Helper function to clean legend labels
def fix_labels(df):
    df['Medicaid Status'] = df['medicaid_expansion'].map({0: 'Non-Expansion', 1: 'Expansion'})
    return df

df_filtered = fix_labels(df_filtered)

# --- GRAPH 1: Overall Debt Trends (Urban vs. Rural) ---
plt.figure(figsize=(14, 8))
sns.lineplot(data=df_filtered, x='year', y='share_debt_all', hue='geo_type',
             palette=['#4682B4', '#A52A2A'], linewidth=4, marker='s', markersize=12)

plt.title('Medical Debt Baseline: Urban vs. Rural Counties', fontsize=26, pad=20, fontweight='bold')
plt.ylabel('Share of Population with Medical Debt', fontsize=22)
plt.xlabel('Year', fontsize=22)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.legend(title='Geography', fontsize=18, title_fontsize=20)

plt.savefig('debt_trend_geo.pdf', format='pdf', bbox_inches='tight')
print("Saved: debt_trend_geo.pdf")

# --- GRAPH 2: The Interaction (FacetGrid: Urban vs. Rural) ---
# Side-by-side comparison of Expansion impact
g = sns.FacetGrid(df_filtered, col="geo_type", col_order=['Urban', 'Rural'],
                  height=7, aspect=0.9, hue="Medicaid Status", palette=['#A52A2A', '#00693e'])

g.map_dataframe(sns.lineplot, x="year", y="share_debt_all", linewidth=4, marker='o', markersize=10)

# Formatting FacetGrid for the poster
g.set_titles("{col_name} Counties", size=24, fontweight='bold')
g.set_axis_labels("Year", "Share of Medical Debt", fontsize=22)

# Adding a vertical line for 2014 in each facet
for ax in g.axes.flat:
    ax.axvline(x=2014, color='black', linestyle='--', alpha=0.7)
    ax.tick_params(labelsize=18)

plt.subplots_adjust(top=0.82, wspace=0.2)
g.fig.suptitle('Expansion Impact: Urban vs. Rural Divergence', fontsize=28, fontweight='bold')
g.add_legend(title="Medicaid Status", fontsize=18, title_fontsize=20)

plt.savefig('debt_geo_interaction.pdf', format='pdf', bbox_inches='tight')
print("Saved: debt_geo_interaction.pdf")

# --- GRAPH 3: Mechanism Check (Hospitalization vs. Debt) ---
df_hosp = df_filtered[df_filtered['year'] <= 2020].dropna(subset=['preventable_hosp_rate', 'share_debt_all'])
sample_data = df_hosp.sample(min(2500, len(df_hosp)))

plt.figure(figsize=(12, 8))
sns.scatterplot(data=sample_data, x='preventable_hosp_rate', y='share_debt_all',
                alpha=0.4, color='#4682B4', s=100)
sns.regplot(data=sample_data, x='preventable_hosp_rate', y='share_debt_all',
            scatter=False, color='#A52A2A', line_kws={"linewidth":5})

plt.title('Mechanism: Preventable Hospitalizations vs. Medical Debt', fontsize=26, pad=20, fontweight='bold')
plt.xlabel('Preventable Hospital Stays (per 100,000 residents)', fontsize=22)
plt.ylabel('Share of Population with Medical Debt', fontsize=22)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)

plt.savefig('hosp_vs_debt_correlation.pdf', format='pdf', bbox_inches='tight')
print("Saved: hosp_vs_debt_correlation.pdf")

plt.show()