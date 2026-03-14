import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

# Load the cleaned 2012-2023 panel for trend analysis
base_path = '/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/'
df = pd.read_csv(os.path.join(base_path, 'data/processed/FINAL_DATASET_V13_NO_HOSP.csv'))

# Calculating yearly averages for the treatment (Expansion) and control (Non-Expansion) groups
# This establishes the national baseline for the medical debt trajectory
trend = (df.groupby(['year', 'medicaid_expansion'])['share_debt_all']
           .mean()
           .reset_index())

exp   = trend[trend['medicaid_expansion'] == 1].sort_values('year')
noexp = trend[trend['medicaid_expansion'] == 0].sort_values('year')

# Visualizing the divergence between expansion and non-expansion states
fig, ax = plt.subplots(figsize=(11, 6))

# Plotting the Expansion group (Policy group)
ax.plot(exp['year'], exp['share_debt_all'],
        color='#1a7abf', marker='o', linewidth=2.4, markersize=7,
        label='Expansion States')

# Plotting the Non-Expansion group (Comparison group)
ax.plot(noexp['year'], noexp['share_debt_all'],
        color='#d94f3d', marker='s', linewidth=2.4, markersize=7,
        label='Non-Expansion States')

# Shading the gap to highlight the increasing policy divergence over time
years_common = sorted(set(exp['year']) & set(noexp['year']))
exp_vals   = exp.set_index('year').loc[years_common, 'share_debt_all']
noexp_vals = noexp.set_index('year').loc[years_common, 'share_debt_all']
ax.fill_between(years_common, exp_vals, noexp_vals,
                alpha=0.10, color='gray', label='Gap between groups')

# Reference marker for the 2014 ACA implementation threshold
ax.axvline(2013.5, color='darkgray', linestyle='--', linewidth=1.4)
ax.text(2013.6, ax.get_ylim()[1] if ax.get_ylim()[1] else 0.26,
        'ACA Expansion\nBegins (2014)',
        fontsize=9.5, color='dimgray', va='top')

# Formatting axes for professional publication standards
ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=0))
ax.set_xticks(sorted(df['year'].unique()))
ax.set_xticklabels(sorted(df['year'].unique()), fontsize=10)
ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('Average Share of Population with Medical Debt', fontsize=12)
ax.set_title('Medical Debt Over Time:\nMedicaid Expansion vs. Non-Expansion States',
             fontsize=15, fontweight='bold', pad=14)
ax.legend(fontsize=11)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()

# Save the trend visualization for the final report
output_path = os.path.join(base_path, 'figures/medicaid_trend_line_not_best.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.show()
print(f"Plot saved to: {output_path}")

# Log summary values to verify the numerical divergence shown in the chart
print("\n--- Average Share with Medical Debt by Year ---")
summary = pd.DataFrame({
    'Expansion':     exp.set_index('year')['share_debt_all'],
    'Non-Expansion': noexp.set_index('year')['share_debt_all'],
})
summary['Gap (Non - Exp)'] = summary['Non-Expansion'] - summary['Expansion']
print((summary * 100).round(2).to_string())