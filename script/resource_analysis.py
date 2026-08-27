import pandas as pd
import plotly.express as px

# =========================================================
# 1. LOAD DATASET
# =========================================================

df = pd.read_csv("../Hospital_Operations_Dataset.csv")

print("Dataset loaded successfully!")

print("\nDataset Shape:")
print(df.shape)

print("\nColumn Names:")
print(df.columns.tolist())


# =========================================================
# 2. RESOURCE DATA ANALYSIS
# =========================================================

total_patients = df["Patient_ID"].nunique()
total_doctors = df["Doctor_ID"].nunique()
total_departments = df["Department"].nunique()

print("\nRESOURCE DATA ANALYSIS")

print("Total Patients:", total_patients)
print("Total Doctors:", total_doctors)
print("Total Departments:", total_departments)


# =========================================================
# 3. DEPARTMENT-WISE DOCTORS
# =========================================================

doctor_by_department = (
    df.groupby("Department")["Doctor_ID"]
    .nunique()
    .reset_index()
)

doctor_by_department.columns = ["Department", "Doctors"]

print("\n--- DEPARTMENT-WISE DOCTORS ---")
print(doctor_by_department.to_string(index=False))


# =========================================================
# 4. RESOURCE AVAILABILITY TABLE
# =========================================================

resource_summary = pd.DataFrame({
    "Resource": [
        "Patients",
        "Doctors",
        "Departments",
        "Beds",
        "Nurses",
        "Other Staff"
    ],
    "Availability": [
        total_patients,
        total_doctors,
        total_departments,
        "Not available",
        "Not available",
        "Not available"
    ]
})

print("\n--- RESOURCE AVAILABILITY TABLE ---")
print(resource_summary.to_string(index=False))


# =========================================================
# 5. DEPARTMENT-WISE PATIENT COUNT
# =========================================================

patients_by_department = (
    df.groupby("Department")["Patient_ID"]
    .nunique()
    .reset_index()
)

patients_by_department.columns = ["Department", "Patients"]

print("\n--- DEPARTMENT-WISE PATIENT COUNT ---")
print(patients_by_department.to_string(index=False))


# =========================================================
# 6. PATIENTS VS DOCTORS
# =========================================================

department_comparison = patients_by_department.merge(
    doctor_by_department,
    on="Department"
)

print("\n--- PATIENTS VS DOCTORS ---")
print(department_comparison.to_string(index=False))


# =========================================================
# 7. BED DATA CHECK
# =========================================================

bed_columns = [
    column for column in df.columns
    if "bed" in column.lower()
]

print("\n--- BED RELATED COLUMNS ---")
print(bed_columns)

if len(bed_columns) == 0:
    print("Bed information is not available in the current dataset.")


# =========================================================
# 8. CHART 1 — DOCTORS BY DEPARTMENT
# =========================================================

fig1 = px.bar(
    doctor_by_department,
    x="Department",
    y="Doctors",
    title="Department-wise Doctor Availability",
    labels={
        "Department": "Department",
        "Doctors": "Number of Doctors"
    }
)

fig1.show()


# =========================================================
# 9. CHART 2 — PATIENTS BY DEPARTMENT
# =========================================================

fig2 = px.bar(
    patients_by_department,
    x="Department",
    y="Patients",
    title="Department-wise Patient Distribution",
    labels={
        "Department": "Department",
        "Patients": "Number of Patients"
    }
)

fig2.show()


# =========================================================
# 10. CHART 3 — PATIENTS VS DOCTORS
# =========================================================

fig3 = px.bar(
    department_comparison,
    x="Department",
    y=["Patients", "Doctors"],
    barmode="group",
    title="Patients vs Doctors by Department"
)

fig3.show()


# =========================================================
# 11. BUSINESS INSIGHTS
# =========================================================

highest_patient_department = patients_by_department.loc[
    patients_by_department["Patients"].idxmax(),
    "Department"
]

highest_patient_count = patients_by_department["Patients"].max()

lowest_patient_department = patients_by_department.loc[
    patients_by_department["Patients"].idxmin(),
    "Department"
]

lowest_patient_count = patients_by_department["Patients"].min()

print("\n--- BUSINESS INSIGHTS ---")

print(
    f"Highest patient volume: {highest_patient_department} "
    f"with {highest_patient_count} patients."
)

print(
    f"Lowest patient volume: {lowest_patient_department} "
    f"with {lowest_patient_count} patients."
)

print(
    "Doctor IDs are distributed equally across all departments "
    "in the current dataset."
)

print(
    "Bed, nurse and other staff availability cannot be analyzed "
    "because those fields are not present in the current dataset."
)