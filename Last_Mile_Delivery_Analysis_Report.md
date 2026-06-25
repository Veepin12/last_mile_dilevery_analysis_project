# Last-Mile Delivery Analysis Report

This report summarizes the findings from the operational and statistical analysis of a full year of simulated delivery orders across 10 Indian cities (2,080 rows).

## 🛠️ Data Cleaning Summary
Before performing the analysis, the following cleaning steps were executed on the raw dataset:
1. **City Names**: Cleaned leading/trailing spaces and spelling variations:
   - `'delhi'` and `'Delhi'` -> `Delhi`
   - `'chennai'` and `'chennai'` -> `Chennai`
   - `'MUMBAI'` and `'Mumbai'` -> `Mumbai`
   - `'Bangaluru'` and `'Bangalore'` -> `Bangalore`
   - `'Hydrabad'` and `'Hyderabad'` -> `Hyderabad`
   - `' Ahmedabad'` and `'Ahmedabad'` -> `Ahmedabad`
   - `'Kolkata '` and `'Kolkata'` -> `Kolkata`
2. **Vehicle Types**: Standardized capitalization (e.g. `AUTO`, `auto` -> `Auto`, `BIKE`, `bike` -> `Bike`).
3. **Actual Delivery Minutes**: Removed the string `' mins'` from entries (e.g., `'58.6 mins'` -> `58.6`) and cast the column as a floating-point numeric type.
4. **Distance Outliers**: Identified exactly 41 records with physically impossible distances (e.g., 269 km to 488 km delivered in less than 60 minutes) indicating standard coordinate calculation scale issues.

---

## ⏰ Q1 — After Cleaning — Peak Hour Delay Pattern
### Question
*Do orders placed during 8–10 AM and 5–8 PM have significantly higher `delay_mins` than off-peak hours? Quantify the difference.*

### Results & Statistics
- **Peak Hours** (8:00–10:00 AM, 5:00–8:00 PM): 639 orders
- **Off-Peak Hours**: 1,441 orders

| Metric | Peak Hours | Off-Peak Hours | Net Difference |
| :--- | :--- | :--- | :--- |
| **Mean Delay** | 23.95 minutes | 9.60 minutes | **+14.35 minutes** |
| **Median Delay** | 21.10 minutes | 7.20 minutes | **+13.90 minutes** |

- **Two-Sample T-test**: $t = 14.56$, $p$-value = $8.43 \times 10^{-42}$
- **Mann-Whitney U test**: $U = 708764$, $p$-value = $3.97 \times 10^{-44}$

**Key Takeaway**: The differences in delays are **highly statistically significant** ($p \ll 0.05$). Orders placed during peak traffic hours experience median delays that are **nearly 3 times higher** than off-peak hours, adding an average of ~14 minutes to delivery times.

---

## 🌦️ Q2 — EDA — Weather vs Delay Correlation
### Questions
*How does median delay vary across Clear, Rain, and Fog conditions? Which order_type is hit hardest by rain?*

### Results
#### 1. Delay Variation by Weather Condition
Adverse weather conditions are the primary drivers of extreme operational delays:
- **Partly Cloudy**: Median Delay of **5.5 minutes** (400 orders)
- **Clear**: Median Delay of **6.1 minutes** (1,091 orders)
- **Rain**: Median Delay of **29.4 minutes** (422 orders)
- **Fog**: Median Delay of **37.9 minutes** (167 orders)

#### 2. Order Type Hit Hardest by Rain
Comparing Rain and Clear median delays across each order category:

| Order Type | Clear Median Delay (mins) | Rain Median Delay (mins) | Net Median Increase (mins) |
| :--- | :---: | :---: | :---: |
| **Medicine** | 7.70 | 34.65 | **+26.95** |
| **Apparel** | 1.20 | 27.10 | **+25.90** |
| **Electronics** | 3.40 | 28.80 | **+25.40** |
| **Grocery** | 5.00 | 29.05 | **+24.05** |
| **Documents** | 7.20 | 29.80 | **+22.60** |
| **Food** | 6.90 | 29.20 | **+22.30** |

**Key Takeaway**: **Medicine** is hit hardest by rain. It suffers both the **highest absolute median delay in rain (34.65 mins)** and the **largest net delay increase (+26.95 mins)** compared to clear conditions.

---

## 🔑 Q3 — Statistics — Rider Experience Effect
### Question
*Is there a statistically meaningful difference in `delay_mins` between riders with under 2 years experience vs over 4 years?*

### Results & Statistics
- **Group A (Experience < 2 years)**: 450 riders
- **Group B (Experience > 4 years)**: 1,065 riders

| Metric | Group A (< 2 Years) | Group B (> 4 Years) | Difference (A - B) |
| :--- | :--- | :--- | :--- |
| **Mean Delay** | 13.75 minutes | 14.35 minutes | -0.60 minutes |
| **Median Delay** | 11.60 minutes | 12.20 minutes | -0.60 minutes |

- **Two-Sample T-test (Unequal Variance)**: $t = -0.475$, $p$-value = **0.6347**
- **Mann-Whitney U test**: $U = 236402$, $p$-value = **0.5665**

**Key Takeaway**: Since the $p$-values are far greater than the $0.05$ threshold, there is **no statistically meaningful difference** in delivery delays between experienced and newer riders. Tenure does not drive delivery speed; external factors like traffic and weather dominate.

---

## 🖥️ Q4 — Dashboard — City-Level Performance Board
### Results
An interactive 3-panel dashboard has been built in [dashboard.py](./dashboard.py) with the following insights:

#### Panel 1: City-Wise On-Time Rate
The overall on-time rate is extremely low across all cities, averaging only **35.0%**.
- **Top Performer**: Hyderabad (On-Time Rate: **51.56%**, Median Delay: **4.65 mins**)
- **Worst Performer**: Bangalore (On-Time Rate: **31.08%**, Median Delay: **15.45 mins**)

#### Panel 2: Monthly Delay Trend
Median delays show moderate seasonal variations, peaking in April (**14.70 mins**) and December (**14.00 mins**), while dipping in January (**9.60 mins**).

#### Panel 3: Vehicle Type Comparison
All vehicle types perform relatively similarly, with Autos exhibiting slightly higher median delays (13.2 mins) and Bikes having the highest on-time rate (39.85%).
- **Auto**: Median Delay = 13.2 mins | On-Time Rate = 34.96%
- **Bike**: Median Delay = 11.1 mins | On-Time Rate = 39.85%
- **Cycle**: Median Delay = 11.4 mins | On-Time Rate = 34.34%
- **Van**: Median Delay = 11.9 mins | On-Time Rate = 37.41%

---

## 🎯 The Single Biggest Operational Fix
The core issue causing the abysmal **35.0%** overall on-time rate is **rigid, static SLA targets (30-60 minutes)** that do not adjust for highly predictable disruptions. 

### Key Proof Points:
1. **Peak Hours Drop**: Peak traffic hours cause median delays to rise from **7.2 mins to 21.1 mins**, dropping on-time rates to **18.9%**.
2. **Weather Drop**: Fog drops on-time rates to **4.19%** (median delay **37.9 mins**) and Rain drops it to **10.66%** (median delay **29.4 mins**).
3. **Compound Failures**: During peak hours in the rain, the on-time rate is **1.56%**. During peak hours in the fog, it is **0.00%** (100% of deliveries are delayed).
4. **Lack of Internal Drivers**: Delays have zero correlation with distance ($r = -0.021$), rider rating ($r = -0.026$), or rider experience ($r = -0.000$).

### Recommended Operational Fix: **Dynamic SLA Buffers**
Instead of promising fixed 30- or 60-minute delivery times, the system must dynamically adjust promised times at order placement:
* **Peak Hour Buffer**: Automatically add **+15 minutes** to SLAs during 8–10 AM and 5–8 PM.
* **Weather Buffer**: Automatically add **+25 minutes** during Rain and **+35 minutes** during Fog.

**Impact**:
* Corrects customer expectations to align with real-world traffic and weather constraints.
* Instantly lifts the on-time rate metrics to realistic levels.
* Protects rider safety by eliminating the pressure to speed through heavy traffic and hazardous weather to meet unrealistic 30-minute delivery promises.

---

## 🚀 How to Run the Interactive Dashboard

To launch and run the Streamlit dashboard step-by-step, follow these instructions:

### 1. Navigate to Project Directory
Open your terminal and ensure you are in the project's root folder:
```bash
cd /Users/veepinchaudhary8115/Documents/GitHub/last_mile_dilevery_analysis_project
```

### 2. Activate the Virtual Environment
Activate the pre-configured Python virtual environment:
* **macOS/Linux**:
  ```bash
  source .venv/bin/activate
  ```
* **Windows** (Command Prompt):
  ```cmd
  .venv\Scripts\activate.bat
  ```
* **Windows** (PowerShell):
  ```powershell
  .venv\Scripts\Activate.ps1
  ```

### 3. Install Required Packages
Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### 4. Start the Dashboard
Run the Streamlit application:
```bash
streamlit run dashboard.py
```

### 5. Open in Web Browser
Streamlit will automatically open the app in your default browser. If it doesn't, navigate to:
- **Local URL**: `http://localhost:8501` (or `http://localhost:8502` if port 8501 is already in use)

