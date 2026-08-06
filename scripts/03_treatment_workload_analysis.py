import pandas as pd
import os
import plotly.express as px

# ==========================================
# Project Paths
# ==========================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "medical_operations_master.csv"
)

CHARTS_DIR = os.path.join(BASE_DIR, "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)

# ==========================================
# Load Dataset
# ==========================================
master = pd.read_csv(DATA_PATH)

print("=" * 60)
print("MEDICAL OPERATIONS MASTER DATASET")
print("=" * 60)

print("Rows :", master.shape[0])
print("Columns :", master.shape[1])

print("\nFirst 5 Rows:\n")
print(master.head())
# ==========================================
# KPI CALCULATIONS
# ==========================================

total_patients = master["Patient_ID"].nunique()
total_doctors = master["Doctor_ID"].nunique()

patient_doctor_ratio = round(total_patients / total_doctors, 2)

average_treatment_duration = round(
    master["Length_of_Stay_Days"].mean(), 2
)

average_wait_time = round(
    master["Wait_Time_Minutes"].mean(), 2
)

total_treatment_cost = round(master["Treatment_Cost_USD"].sum(), 2)

print("\n")
print("=" * 60)
print("KEY PERFORMANCE INDICATORS (KPIs)")
print("=" * 60)

print(f"Total Patients            : {total_patients:,}")
print(f"Total Doctors             : {total_doctors}")
print(f"Patient-Doctor Ratio      : {patient_doctor_ratio}")
print(f"Average Treatment Duration (Days): {average_treatment_duration}")
print(f"Average Wait Time (Min)   : {average_wait_time}")
print(f"Total Treatment Cost (USD): ${total_treatment_cost:,.0f}")

# ==========================================
# Doctor Workload Analysis
# ==========================================

doctor_workload = (
    master.groupby("Doctor_Name")
    .agg(
        Patients_Treated=("Patient_ID", "count"),
        Average_Stay_Days=("Length_of_Stay_Days", "mean"),
        Total_Treatment_Cost=("Treatment_Cost_USD", "sum")
    )
    .reset_index()
)
doctor_workload["Average_Stay_Days"] = doctor_workload["Average_Stay_Days"].round(2)

# Sort by number of patients
doctor_workload = doctor_workload.sort_values(
    by="Patients_Treated",
    ascending=False
)

print("\n")
print("=" * 60)
print("TOP 10 BUSIEST DOCTORS")
print("=" * 60)

print(doctor_workload.head(10))
doctor_workload.to_csv(
    os.path.join(CHARTS_DIR, "doctor_workload.csv"),
    index=False
)
# ==========================================
# Plotly Chart - Top 10 Busiest Doctors
# ==========================================

top10_doctors = doctor_workload.head(10)

doctor_fig = px.bar(
    top10_doctors,
    x="Doctor_Name",
    y="Patients_Treated",
    color="Patients_Treated",
    title="Top 10 Busiest Doctors",
    text="Patients_Treated",
    color_continuous_scale="Blues"
)

doctor_fig.update_layout(
    xaxis_title="Doctor Name",
    yaxis_title="Patients Treated",
    title_x=0.5,
    template="plotly_white"
)

doctor_fig.write_html(
    os.path.join(CHARTS_DIR, "doctor_workload.html")
)

doctor_fig.show()
# ==========================================
# Department Workload Analysis
# ==========================================

department_workload = (
    master.groupby("Department_Patient")
    .agg(
        Patients=("Patient_ID", "count"),
        Average_Stay_Days=("Length_of_Stay_Days", "mean"),
        Average_Wait_Time=("Wait_Time_Minutes", "mean"),
        Total_Treatment_Cost=("Treatment_Cost_USD", "sum")
    )
    .reset_index()
)

# Round averages
department_workload["Average_Stay_Days"] = department_workload["Average_Stay_Days"].round(2)
department_workload["Average_Wait_Time"] = department_workload["Average_Wait_Time"].round(2)

# Sort by number of patients
department_workload = department_workload.sort_values(
    by="Patients",
    ascending=False
)

print("\n")
print("=" * 60)
print("DEPARTMENT WORKLOAD")
print("=" * 60)

print(department_workload)
department_workload.to_csv(
    os.path.join(CHARTS_DIR, "department_workload.csv"),
    index=False
)
# ==========================================
# Plotly Chart - Department Workload
# ==========================================

department_fig = px.bar(
    department_workload,
    x="Department_Patient",
    y="Patients",
    color="Patients",
    title="Department Workload",
    text="Patients",
    color_continuous_scale="Viridis"
)

department_fig.update_layout(
    xaxis_title="Department",
    yaxis_title="Number of Patients",
    title_x=0.5,
    template="plotly_white"
)

department_fig.write_html(
    os.path.join(CHARTS_DIR, "department_workload.html")
)

department_fig.show()
# ==========================================
# Treatment Counts Analysis
# ==========================================

treatment_counts = (
    master.groupby("Diagnosis")
    .agg(
        Total_Patients=("Patient_ID", "count")
    )
    .reset_index()
)

# Sort from highest to lowest
treatment_counts = treatment_counts.sort_values(
    by="Total_Patients",
    ascending=False
)

print("\n")
print("=" * 60)
print("TREATMENT COUNTS")
print("=" * 60)

print(treatment_counts)
treatment_counts.to_csv(
    os.path.join(CHARTS_DIR, "treatment_counts.csv"),
    index=False
)
# ==========================================
# Plotly Chart - Treatment Counts
# ==========================================

treatment_fig = px.bar(
    treatment_counts,
    x="Diagnosis",
    y="Total_Patients",
    color="Total_Patients",
    title="Treatment Counts by Diagnosis",
    text="Total_Patients",
    color_continuous_scale="Plasma"
)

treatment_fig.update_layout(
    xaxis_title="Diagnosis",
    yaxis_title="Number of Patients",
    title_x=0.5,
    template="plotly_white"
)

treatment_fig.write_html(
    os.path.join(CHARTS_DIR, "treatment_counts.html")
)

treatment_fig.show()
# ==========================================
# Average Treatment Duration Analysis
# ==========================================

avg_treatment_duration = (
    master.groupby("Department_Patient")
    .agg(
        Average_Stay_Days=("Length_of_Stay_Days", "mean")
    )
    .reset_index()
)

# Round to 2 decimal places
avg_treatment_duration["Average_Stay_Days"] = (
    avg_treatment_duration["Average_Stay_Days"].round(2)
)

# Sort from highest to lowest
avg_treatment_duration = avg_treatment_duration.sort_values(
    by="Average_Stay_Days",
    ascending=False
)

print("\n")
print("=" * 60)
print("AVERAGE TREATMENT DURATION")
print("=" * 60)

print(avg_treatment_duration)
avg_treatment_duration.to_csv(
    os.path.join(CHARTS_DIR, "average_treatment_duration.csv"),
    index=False
)
# ==========================================
# Plotly Chart - Average Treatment Duration
# ==========================================

avg_treatment_duration_fig = px.bar(
    avg_treatment_duration,
    x="Department_Patient",
    y="Average_Stay_Days",
    color="Average_Stay_Days",
    title="Average Treatment Duration by Department",
    text="Average_Stay_Days",
    color_continuous_scale="Teal"
)

avg_treatment_duration_fig.update_layout(
    xaxis_title="Department",
    yaxis_title="Average Stay (Days)",
    title_x=0.5,
    template="plotly_white"
)

avg_treatment_duration_fig.write_html(
    os.path.join(CHARTS_DIR, "average_treatment_duration.html")
)

avg_treatment_duration_fig.show()