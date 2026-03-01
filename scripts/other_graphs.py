import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 1. Load your Master Dataset
# Ensure your filename matches exactly what is in your folder
df = pd.read_csv('FINAL_DATASET_V13_MASTER.csv')

# --- GRAPH 1: RACIAL EQUITY & EXPANSION ---
# We split counties into "High % POC" and "Low % POC" based on the median
df['poc_category'] = np.where(df['pct_poc'] > df['pct_poc'].median(), 'High % POC', 'Low % POC')

plt.figure(figsize=(12, 6))
# Style='medicaid_expansion' creates dashed lines for non-expansion and solid for expansion
sns.lineplot(data=df, x='year', y='share_debt_all', hue='poc_category',
             style='medicaid_expansion', markers=True, dashes=True)

plt.axvline(x=2014, color='red', linestyle='--', label='ACA Expansion Start')
plt.title('Medical Debt Trends: Impact of Medicaid Expansion on Racial Equity')
plt.ylabel('Share of Population with Medical Debt')
plt.xlabel('Year')
plt.legend(title='Category & Expansion Status', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('debt_race_interaction.png')
print("Saved: debt_race_interaction.png")


# --- GRAPH 2: DRIVERS OF DEBT (CORRELATION HEATMAP) ---
# We select the most important numeric variables to see how they relate to debt
numeric_cols = [
    'share_debt_all', 'median_income', 'unemployment_rate',
    'median_age', 'pct_65_plus', 'uninsured_rate',
    'pct_poc', 'preventable_hosp_rate'
]
# Calculate the correlation matrix
corr_matrix = df[numeric_cols].corr()

plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
plt.title('Correlation Heatmap: What Drives Medical Debt?')
plt.tight_layout()
plt.savefig('debt_correlation_heatmap.png')
print("Saved: debt_correlation_heatmap.png")


# --- GRAPH 3: THE UNEMPLOYMENT SHOCK (RESILIENCE PLOT) ---
plt.figure(figsize=(10, 6))
# Using a sample of 3000 rows so the computer doesn't lag
# 'lmplot' creates the scatter points + the regression line
plot = sns.lmplot(data=df.sample(3000), x='unemployment_rate', y='share_debt_all',
                  hue='medicaid_expansion', aspect=1.5,
                  scatter_kws={'alpha':0.2}, palette='viridis')

# Rename labels for clarity
new_title = 'The Unemployment-to-Debt Pipeline'
plot.fig.suptitle(new_title, y=1.05)
plot.set_axis_labels("Unemployment Rate (%)", "Share of Medical Debt")
plot._legend.set_title("Medicaid Expansion")

plt.savefig('unemployment_debt_shock.png')
print("Saved: unemployment_debt_shock.png")

# Final command to show all plots if running in a windowed environment
plt.show()