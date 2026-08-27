import pandas as pd
import numpy as np
import plotly.express as px

df = pd.read_csv("Hospital_Operations_Dataset.csv")

print(df.head())
print("\nDataset Shape:")
print(df.shape)

print("\nColumn Names:")
print(df.columns.tolist())

print("\nMissing Values:")
print(df.isnull().sum())
print("\nDepartment-wise Patient Count:")
print(df["Department"].value_counts())

print("\nDiagnosis-wise Patient Count:")
print(df["Diagnosis"].value_counts())

print("\nOutcome-wise Patient Count:")
print(df["Outcome"].value_counts())
print("\nAverage Length of Stay:")
print(df["Length_of_Stay_Days"].mean())

print("\nAverage Wait Time (Minutes):")
print(df["Wait_Time_Minutes"].mean())

print("\nAverage Treatment Cost (USD):")
print(df["Treatment_Cost_USD"].mean())

print("\nReadmission Rate:")
print(df["Readmission_Flag"].mean() * 100)
import plotly.express as px

# 1. Patients by Department
department_count = df["Department"].value_counts().reset_index()
department_count.columns = ["Department", "Patient_Count"]

fig1 = px.bar(
    department_count,
    x="Department",
    y="Patient_Count",
    title="Patients by Department"
)

fig1.show()


# 2. Patient Outcomes
outcome_count = df["Outcome"].value_counts().reset_index()
outcome_count.columns = ["Outcome", "Patient_Count"]

fig2 = px.pie(
    outcome_count,
    names="Outcome",
    values="Patient_Count",
    title="Patient Outcomes"
)

fig2.show()


# 3. Average Treatment Cost by Department
department_cost = (
    df.groupby("Department")["Treatment_Cost_USD"]
      .mean()
      .reset_index()
      .sort_values("Treatment_Cost_USD")
)

fig3 = px.bar(
    department_cost,
    x="Department",
    y="Treatment_Cost_USD",
    title="Average Treatment Cost by Department"
)

fig3.show()
print("\nDischarge Time Values:")
print(df["Discharge_Time"].head(10))

print("\nOutcome Counts:")
print(df["Outcome"].value_counts())

print("\nLength of Stay Statistics:")
print(df["Length_of_Stay_Days"].describe())
# Discharge Trend

df["Admit_Date"] = pd.to_datetime(
    df["Admit_Date"],
    format="%d-%m-%Y"
)

df["Month"] = df["Admit_Date"].dt.to_period("M").astype(str)

monthly_outcome = (
    df.groupby(["Month", "Outcome"])
      .size()
      .reset_index(name="Patient_Count")
)

fig4 = px.line(
    monthly_outcome,
    x="Month",
    y="Patient_Count",
    color="Outcome",
    markers=True,
    title="Monthly Patient Outcome Trend"
)

fig4.show()
# Discharge Rate by Department

department_discharge = (
    df.groupby("Department")
      .size()
      .reset_index(name="Total_Patients")
)

discharged = (
    df[df["Outcome"].isin(["Recovered", "Improved"])]
    .groupby("Department")
    .size()
    .reset_index(name="Discharged_Patients")
)

department_discharge = department_discharge.merge(
    discharged,
    on="Department",
    how="left"
)

department_discharge["Discharge_Rate"] = (
    department_discharge["Discharged_Patients"]
    / department_discharge["Total_Patients"]
    * 100
)

fig5 = px.bar(
    department_discharge.sort_values("Discharge_Rate"),
    x="Department",
    y="Discharge_Rate",
    title="Discharge Rate by Department",
    labels={"Discharge_Rate": "Discharge Rate (%)"}
)

fig5.show()
# Average Length of Stay by Department

avg_stay = (
    df.groupby("Department")["Length_of_Stay_Days"]
      .mean()
      .reset_index()
)

fig6 = px.bar(
    avg_stay.sort_values("Length_of_Stay_Days"),
    x="Department",
    y="Length_of_Stay_Days",
    title="Average Length of Stay by Department",
    labels={
        "Length_of_Stay_Days": "Average Length of Stay (Days)"
    }
)

fig6.show()
# Discharge Efficiency by Department

efficiency = (
    df.groupby("Department")
      .agg(
          Total_Patients=("Patient_ID", "count"),
          Successful_Discharges=("Outcome", lambda x: x.isin(["Recovered", "Improved"]).sum())
      )
      .reset_index()
)

efficiency["Discharge_Efficiency"] = (
    efficiency["Successful_Discharges"]
    / efficiency["Total_Patients"]
    * 100
)

fig7 = px.bar(
    efficiency.sort_values("Discharge_Efficiency"),
    x="Department",
    y="Discharge_Efficiency",
    title="Discharge Efficiency by Department",
    labels={
        "Discharge_Efficiency": "Discharge Efficiency (%)"
    }
)

fig7.show()