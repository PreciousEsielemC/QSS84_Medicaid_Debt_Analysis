"""
event_study_v2.py
=================
Run this script from the scripts/ folder.

This version estimates the event study by manually building the design matrix
instead of using PanelOLS.from_formula(). Doing it this way avoids issues with
column naming and keeps the regression inputs explicit.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')          # allows the script to run without opening a GUI window
import matplotlib.pyplot as plt
from linearmodels.panel import PanelOLS
from scipy import stats
import os, warnings
warnings.filterwarnings('ignore')

# ── CONFIG — main settings for the script ────────────────────────────────────
# These are the paths and parameters that might need changing depending
# on where the project is stored or how wide the event window should be.
BASE   = '/Users/preciousesielem/PycharmProjects/QSS84_Medicaid_Debt_Analysis/'
INFILE = os.path.join(BASE, 'data/processed/FINAL_DATASET_V13_NO_HOSP.csv')
OUTPNG = os.path.join(BASE, 'figures/event_study_v3.png')
OUTPDF = os.path.join(BASE, 'figures/event_study_v3.pdf')

WINDOW   = 4          # number of years before/after expansion to include
REF      = -1         # reference year used for normalization
CONTROLS = ['unemployment_rate', 'median_income']
# ────────────────────────────────────────────────────────────────────────────

print("=" * 60)
print("EVENT STUDY  |  Medicaid Expansion × Rural / Urban")
print("=" * 60)

# ── 1. LOAD DATA ─────────────────────────────────────────────────────────────
# Read in the cleaned dataset that contains the variables used for the event study
df = pd.read_csv(INFILE)
print(f"\nRows: {len(df):,}  |  Counties: {df['fips'].nunique():,}  |  "
      f"Years: {df['year'].min()}–{df['year'].max()}")

# ── 2. BUILD EVENT TIME ──────────────────────────────────────────────────────
# Identify the first year each county experienced Medicaid expansion.
# Counties that never expanded will simply have missing values here.
first_exp = (df[df['medicaid_expansion'] == 1]
             .groupby('fips')['year'].min()
             .rename('treat_year'))
df = df.join(first_exp, on='fips')                 # never-treated counties remain NaN

# Calculate years relative to expansion
df['rel'] = (df['year'] - df['treat_year'])

# Trim the window so extremely early/late years are grouped at the endpoints
df['et']  = df['rel'].clip(-WINDOW, WINDOW)

# Never-treated counties keep NaN values here and act as the control group
print(f"  Ever-treated:  {df['treat_year'].notna()['fips' if False else True] if False else df[df['treat_year'].notna()]['fips'].nunique():,}")
print(f"  Never-treated: {df[df['treat_year'].isna()]['fips'].nunique():,}  (control group)")

# ── 3. CREATE EVENT-TIME DUMMIES ─────────────────────────────────────────────
# Build dummy variables for each relative year except the reference period.
# The omitted year becomes the baseline in the regression.
RYS = [r for r in range(-WINDOW, WINDOW + 1) if r != REF]

for r in RYS:
    col = f'd{r}'          # simple naming (d-4, d-3, ... d1, d2 etc.)
    df[col] = np.where(df['et'] == r, 1.0, 0.0)

DCOLS = [f'd{r}' for r in RYS]
print(f"\nDummies: {DCOLS}  (ref = year {REF})")

# ── 4. ESTIMATION FUNCTION ───────────────────────────────────────────────────
# Runs the event study regression for a given subset of the data
# (used separately for urban and rural counties).
def event_study(subset: pd.DataFrame, label: str) -> pd.DataFrame:
    sub = subset.reset_index(drop=True).copy()
    need = ['fips','year','share_debt_all'] + CONTROLS + DCOLS
    sub  = sub.dropna(subset=need).set_index(['fips','year'])

    Y = sub['share_debt_all']
    X = pd.concat([sub[DCOLS], sub[CONTROLS]], axis=1)
    X.insert(0, 'const', 1.0)

    # TWFE regression with county and year fixed effects
    res = PanelOLS(Y, X, entity_effects=True, time_effects=True)\
              .fit(cov_type='clustered', cluster_entity=True)

    b  = res.params[DCOLS].values
    se = res.std_errors[DCOLS].values

    # Joint test for pre-treatment trends
    pre   = np.array([r < REF for r in RYS])
    pb, ps = b[pre], se[pre]
    chi2  = float(np.sum((pb / np.where(ps>1e-12, ps, 1e-12))**2))
    pval  = float(1 - stats.chi2.cdf(chi2, int(pre.sum())))
    ok    = "✓ PASS" if pval > .05 else "✗ CAUTION"
    print(f"\n[{label}]  Pre-trend χ²({int(pre.sum())}) = {chi2:.3f}  "
          f"p = {pval:.4f}  {ok}")

    # Organize coefficients into a cleaner table and insert the reference year
    out = pd.DataFrame({'ry': RYS, 'b': b, 'se': se})
    out = pd.concat([out, pd.DataFrame({'ry':[REF],'b':[0.],'se':[0.]})])\
            .sort_values('ry').reset_index(drop=True)
    out['lo'] = out['b'] - 1.96*out['se']
    out['hi'] = out['b'] + 1.96*out['se']

    print(out[['ry','b','se','lo','hi']].to_string(index=False))
    return out


print("\n── Urban ──")
urb = event_study(df[df['is_rural']==0].copy(), "Urban")
print("\n── Rural ──")
rur = event_study(df[df['is_rural']==1].copy(), "Rural")

# ── 5. RURAL–URBAN GAP ───────────────────────────────────────────────────────
# Compute the difference between rural and urban coefficients
gap = rur.merge(urb, on='ry', suffixes=('_r','_u'))
gap['g']  = gap['b_r']  - gap['b_u']
gap['gs'] = np.sqrt(gap['se_r']**2 + gap['se_u']**2)
gap['gl'] = gap['g'] - 1.96*gap['gs']
gap['gh'] = gap['g'] + 1.96*gap['gs']
print("\n── Rural − Urban gap ──")
print(gap[['ry','g','gs','gl','gh']].to_string(index=False))

# ── 6. PLOT RESULTS ──────────────────────────────────────────────────────────
# Plot the event study coefficients and confidence intervals
UC, RC, GC = '#2166AC', '#D6604D', '#4DAC26'
RYS_ALL    = sorted(urb['ry'].tolist())
XMN, XMX   = min(RYS_ALL)-.35, max(RYS_ALL)+.35

fig, (a1, a2) = plt.subplots(2, 1, figsize=(12, 10),
                              gridspec_kw={'height_ratios':[3,2],'hspace':.42})

def decorate(ax):
    # Light shading to visually separate pre and post periods
    ax.axvspan(XMN, -.5, alpha=.06, color='gray',  zorder=0)
    ax.axvspan(-.5, XMX, alpha=.05, color='green', zorder=0)
    ax.axvline(-.5, color='#555', ls='--', lw=1.3, label='Expansion Adopted', zorder=3)
    ax.axhline(0,   color='k',    ls='-',  lw=0.8, zorder=3)
    ax.set_xticks(RYS_ALL)
    ax.set_xticklabels([int(y) for y in RYS_ALL], fontsize=10)
    ax.grid(axis='y', alpha=.3, lw=.6)

# Panel A
decorate(a1)
a1.fill_between(urb['ry'], urb['lo'], urb['hi'], alpha=.18, color=UC, zorder=2)
a1.plot(urb['ry'], urb['b'], '-o', color=UC, lw=2, ms=6,
        label='Urban Counties', zorder=4)
a1.fill_between(rur['ry'], rur['lo'], rur['hi'], alpha=.18, color=RC, zorder=2)
a1.plot(rur['ry'], rur['b'], '-s', color=RC, lw=2, ms=6,
        label='Rural Counties', zorder=4)
a1.set_title('Panel A — Event Study: Medicaid Expansion Impact on Medical Debt',
             fontsize=13, fontweight='bold', pad=10)
a1.set_ylabel('Change in Share with Medical Debt\n(β relative to year −1)', fontsize=11)
a1.legend(fontsize=11, loc='lower left')

yl = a1.get_ylim()
a1.text(XMN+.1, yl[0], 'Pre-treatment\n(parallel trends)',
        fontsize=8.5, color='gray', style='italic', va='bottom')
a1.text(.1, yl[0], 'Post-expansion',
        fontsize=8.5, color='#2d6a2d', style='italic', va='bottom')

# Panel B
decorate(a2)
a2.fill_between(gap['ry'], gap['gl'], gap['gh'], alpha=.20, color=GC, zorder=2)
a2.plot(gap['ry'], gap['g'], '-D', color=GC, lw=2, ms=6,
        label='Rural − Urban Gap', zorder=4)
a2.set_title('Panel B — Rural Minus Urban Friction Gap (Dynamic Interaction)',
             fontsize=13, fontweight='bold', pad=10)
a2.set_ylabel('Rural β − Urban β\n(+ve = rural captured less benefit)', fontsize=10)
a2.set_xlabel('Years Relative to Medicaid Expansion Adoption', fontsize=11)
a2.legend(fontsize=11, loc='upper left')

# Small note explaining the model specification
fig.text(.5, .005,
    'Notes: TWFE — county & year FE. Controls: unemployment rate, median income. '
    'SEs clustered at county level. Bands = 95 % CI. Ref year = −1. '
    'Never-treated counties serve as control group.',
    ha='center', fontsize=8.5, color='#444', style='italic')

plt.suptitle('The Rural Friction Gap in Medicaid Expansion: Event Study Evidence',
             fontsize=15, fontweight='bold', y=1.01)

plt.savefig(OUTPNG, dpi=300, bbox_inches='tight')
plt.savefig(OUTPDF,           bbox_inches='tight')
print(f"\nSaved → {OUTPNG}")
print(f"Saved → {OUTPDF}")

print("\nWhat to look for:")
print("  Panel A  pre-period (−4 to −2): both lines near 0 → parallel trends OK")
print("  Panel A  post-period:  Urban drops more than Rural → friction gap")
print("  Panel B: green line near 0 pre, rises positive post → gap compounds over time")