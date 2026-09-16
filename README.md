# 🏥 Medical Operations Dashboard — Team B, Batch 2

An interactive, multi-page Streamlit dashboard that brings together hospital operational data into one place. Built as a combined team effort — each team member contributed their own analysis section, all merged into a single Streamlit UI.

---

## 📌 What This Dashboard Does

Upload your hospital operations CSV from the sidebar and explore 13 analysis sections with live filters. Everything is interactive — filter by date range, department, hospital type, diagnosis, and severity. Charts update instantly.

---

## 📊 Dashboard Sections

| # | Section | What You Get |
|---|---|---|
| 1 | 🏠 Dashboard Overview | Top-level KPIs — total patients, doctors, avg wait time, avg length of stay, total treatment cost |
| 2 | 👥 Patient Flow & Outcomes | Department-wise patient count, avg wait time, avg LOS, diagnosis split, recovery/outcome breakdown |
| 3 | 🏥 Hospital & Facility Analysis | Top hospitals by volume, government vs private split, cost and stay by department |
| 4 | 📅 Admission & Demand Trends | Daily and monthly admission trends, peak days, day-of-week patterns, month-over-month growth |
| 5 | 🚪 Discharge & Recovery Analysis | Overall discharge rate, successful outcomes by department, monthly trend |
| 6 | 📈 Service Demand Analysis | Top 10 diagnoses, monthly service demand, weekday demand, treatment cost by department |
| 7 | 👨‍⚕️ Workforce & Staff Utilization | Doctor/nurse/staff load per department, patients per doctor |
| 8 | 🛏️ Bed Occupancy Analysis | Available vs occupied beds, occupancy rate, department-level bed pressure |
| 9 | 🏢 Department Workload Analysis | Workload distribution, admission vs discharge balance per department |
| 10 | ⚠️ Operational Bottlenecks | SLA breach rates (>3hr wait), discharge delay days, dual bottleneck cases (high wait + high LOS) |
| 11 | 🎯 Resource Capacity & Efficiency | Capacity vs actual demand, efficiency scoring |
| 12 | 📏 Benchmark & Utilization Gap | Performance against clinical benchmarks, utilization gaps |
| 13 | 📊 Capacity Trends & Risk | Trend-based risk flagging for overcapacity departments |
| 14 | 🏆 Hospital Resource Performance | Cross-hospital resource comparison |

---

## 🔎 Sidebar Filters

All sections respond to these filters applied from the sidebar:

- **Date range** — admission date window
- **Department** — single or multi-select
- **Hospital Type** — government / private
- **Diagnosis** — filter by specific condition
- **Severity Level** — filter by patient severity

Record count after filtering is shown live in the sidebar.

---

## 🚀 How to Run

**Install dependencies**
```bash
pip install streamlit pandas numpy plotly
```

**Launch the app**
```bash
streamlit run app.py
```

**Upload your data**
Use the sidebar uploader to load your hospital CSV. The dashboard works with the shared master dataset or any compatible CSV.
🔗 [Open Medical Operations Dashboard](https://medicaloperationsdashboard.streamlit.app/)

---

## 📋 What Columns the Dashboard Expects

The app auto-detects column names — no renaming needed if your CSV follows these conventions:

| Data Type | Accepted Column Names |
|---|---|
| Patient ID | `Patient_ID`, `PatientID` |
| Department | `Department_Patient`, `Department` |
| Admission Date | `Admission_Date`, `Admit_Date` |
| Discharge Date | `Discharge_Date`, `Discharge_Time` |
| Wait Time | `Wait_Time_Minutes` |
| Length of Stay | `Length_of_Stay_Days`, `LOS_Days` |
| Treatment Cost | `Treatment_Cost_INR`, `Treatment_Cost_USD` |
| Doctor | `Doctor_Name`, `Doctor_ID` |
| Nurse / Staff | `Nurse_Name`, `Staff_Name` |
| Hospital | `Hospital_Name`, `Hospital_Type` |
| Beds | `Total_Beds`, `Available_Beds`, `Occupied_Beds` |
| Clinical | `Diagnosis`, `Severity_Level`, `Outcome` |
| Readmission | `Readmission_Flag`, `Readmission_30_Days` |

If a column isn't found, that specific chart is skipped — no errors, no crashes.

---

## 👥 Team

**Team B — Batch 2**
Each team member worked on a separate task and folder. This `app.py` combines all individual contributions into one unified Streamlit dashboard.

---

## 🛠️ Tech Stack

- **Streamlit** — UI and page navigation
- **Plotly Express** — all interactive charts
- **Pandas / NumPy** — data processing and feature engineering
- **Python 3.x**
