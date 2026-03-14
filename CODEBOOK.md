# Codebook  
## The Impact of Medicaid Expansion on Medical Debt

**Project:** Geographic Disparities in Medical Debt and the "Rural Friction Gap"  
**Author:** Precious Esielem  
**Institution:** Dartmouth College — Department of Quantitative Social Science  
**Study Period:** 2012–2023  

---

# Project Description

This dataset evaluates the impact of the **Affordable Care Act (ACA) Medicaid Expansion** on **county-level medical debt in collections** across the United States from **2012–2023**.  

The analysis focuses on:

- **Urban–rural disparities**
- **Healthcare infrastructure constraints**
- **Mechanisms linking insurance expansion to financial outcomes**

The dataset integrates multiple national administrative and survey sources including the **Urban Institute**, **U.S. Census Bureau**, **Kaiser Family Foundation**, **USDA ERS**, **County Health Rankings**, and the **Chartis Center for Rural Health**.

---

# I. Primary Outcome Variable

### `share_debt_all`

**Definition**  
Proportion of the adult population with at least one **medical debt account in collections**.

**Measurement**

Decimal percentage  
Example:

0.15 = 15% of adults in the county have medical debt in collections


**Source**

Urban Institute — *Debt in America*

https://apps.urban.org/features/debt-interactive-map/

---

# II. Policy & Geographic Variables

### `medicaid_expansion`

**Definition**  
Indicates whether a state implemented the ACA Medicaid expansion in a given year.

**Measurement**

Binary

| Value | Meaning |
|-----|-----|
| 1 | State adopted Medicaid Expansion |
| 0 | State did not expand Medicaid |

**Source**

Kaiser Family Foundation (KFF)

https://www.kff.org/medicaid/issue-brief/status-of-state-medicaid-expansion-decisions-interactive-map/

---

### `rucc_2013`

**Definition**

USDA **Rural–Urban Continuum Codes**, which classify counties by population size and proximity to metropolitan areas.

**Measurement**

Integer scale:


1 – 3 Metropolitan counties
4 – 9 Nonmetropolitan counties


**Source**

USDA Economic Research Service

https://www.ers.usda.gov/data-products/rural-urban-continuum-codes/

---

### `geo_type`

**Definition**

Simplified geographic classification derived from **RUCC codes**.

**Measurement**

Categorical

| Category | RUCC Codes |
|------|------|
| Urban | 1–3 |
| Suburban | 4–6 |
| Rural | 7–9 |

**Source**

Derived from USDA RUCC classifications.

---

### `is_rural`

**Definition**

Binary indicator identifying counties classified as rural for regression interaction models.

**Measurement**

| Value | Meaning |
|------|------|
| 1 | Rural county |
| 0 | Non-rural county |

**Construction**

Derived from RUCC codes **4–9**.

---

# III. Mechanism Variables

### `ever_closed`

**Definition**

Indicates whether a county experienced **at least one rural hospital closure** during the study period.

**Measurement**

Binary

| Value | Meaning |
|------|------|
| 1 | County had ≥1 rural hospital closure |
| 0 | No rural hospital closures |

**Source**

Chartis Center for Rural Health  
Chartis Rural Hospital Closure Tracker

https://www.chartis.com/vantage-points/rural-hospital-closures-continue-mount

---

### `hospital_closure_status`

**Definition**

Categorical classification used for **split-sample heterogeneity analysis**.

**Categories**

| Category | Description |
|------|------|
| Rural – Closure | Rural county with ≥1 hospital closure |
| Rural – No Closure | Rural county with no closures |
| Urban | Non-rural counties |

---

### `preventable_hosp_rate`

**Definition**

Rate of **preventable hospital stays** for conditions typically treatable in outpatient settings (e.g., asthma, diabetes).

Used as a proxy for **local healthcare infrastructure strain**.

**Measurement**

Rate per **100,000 Medicare enrollees**

**Source**

County Health Rankings & Roadmaps

https://www.countyhealthrankings.org/explore-health-rankings/rankings-data-documentation

---

# IV. Control Variables (Covariates)

### `unemployment_rate`

**Definition**

Percentage of the local labor force that is unemployed.

**Measurement**

Percentage

Example:


5.4 = 5.4% unemployment


**Source**

Bureau of Labor Statistics via County Health Rankings  
Census Equivalent Table: **ACS S2301**

https://data.census.gov/table/ACSST5Y2022.S2301

---

### `median_income`

**Definition**

Median household income in the county.

**Measurement**

USD

**Source**

American Community Survey (ACS)

Table: **B19013 – Median Household Income**

https://data.census.gov/table/ACSDT5Y2022.B19013

---

### `uninsured_rate`

**Definition**

Percentage of the population under age 65 without health insurance coverage.

**Measurement**

Decimal percentage

Example:


0.12 = 12% uninsured


**Source**

U.S. Census Bureau  
Small Area Health Insurance Estimates (SAHIE)

https://www.census.gov/programs-surveys/sahie.html

---

### `pct_poc`

**Definition**

Percentage of the population identifying as **People of Color (Non-White)**.

**Measurement**

Percentage

**Construction**

Derived from:

ACS Table **B03002 – Hispanic or Latino Origin by Race**

Calculated as:


Total Population − White Alone (Non-Hispanic)


https://data.census.gov/table/ACSDT5Y2022.B03002

---

### `median_age`

**Definition**

Median age of the county population.

**Measurement**

Years

Example:


37.0 = median age 37


**Source**

ACS Table **B01002 – Median Age by Sex**

https://data.census.gov/table/ACSDT5Y2022.B01002

---

### `pct_65_plus`

**Definition**

Percentage of the population aged **65 and older**.

**Measurement**

Percentage

Example:


18.5 = 18.5% of population age 65+


**Source**

ACS Table **DP05 – Demographic and Housing Estimates**

https://data.census.gov/table/ACSDP5Y2022.DP05

---

### Note on Demographic Data

Demographic variables use **ACS 5-Year Estimates** rather than 1-Year estimates because:

- They provide **greater reliability for small counties**
- They ensure **full national county coverage**
- They reduce **data suppression issues in rural areas**

---

# V. Identifiers

### `fips`

**Definition**

Federal Information Processing Standards code uniquely identifying each county.

**Measurement**

5-digit integer

Example:


01001 = Autauga County, Alabama


**Source**

U.S. Census Bureau

---

### `full_name`

**Definition**

Full county name including state.

**Measurement**

String

Example:


Autauga County, Alabama


---

### `year`

**Definition**

Calendar year for the observation.

**Measurement**

Integer

Range:


2012 – 2023


---

# VI. Sample Construction & Attrition Summary

**Initial Dataset**


37,716 observations


(All U.S. counties across 2012–2023)

---

## Cleaning Protocol

### 1. Listwise Deletion

Observations missing key covariates were removed:

- `median_income`
- `unemployment_rate`
- `uninsured_rate`

---

### 2. Geographic Matching

Only counties with valid **FIPS matches across all data sources** were retained.

---

## Final Analytical Sample


35,868 observations


---

## Data Retention Rate


95.1%


---

## Note on Missingness

Most attrition (**4.9%**) is driven by **data suppression in extremely small rural counties** within ACS demographic estimates.

These counties typically have populations too small for reliable demographic estimation.

---