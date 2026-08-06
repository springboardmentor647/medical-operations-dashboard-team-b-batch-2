import pandas as pd
import random
import os
# Make random assignments reproducible
random.seed(42)

# ============================================
# Project Paths
# ============================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
REF_DIR = os.path.join(BASE_DIR, "data", "reference")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

os.makedirs(PROCESSED_DIR, exist_ok=True)

# ============================================
# Load Data
# ============================================
patients = pd.read_csv(os.path.join(RAW_DIR, "Hospital_Operations.csv"))
doctors = pd.read_csv(os.path.join(REF_DIR, "doctors.csv"))
hospitals = pd.read_csv(os.path.join(REF_DIR, "hospitals.csv"))
cities = pd.read_csv(os.path.join(REF_DIR, "cities.csv"))
nurses = pd.read_csv(os.path.join(REF_DIR, "nurses.csv"))

# ============================================
# Merge Patients + Doctors
# ============================================
master = patients.merge(
    doctors,
    on="Doctor_ID",
    how="left",
    suffixes=("_Patient", "_Doctor")
)

# ============================================
# Merge Hospital Details
# ============================================
master = master.merge(
    hospitals,
    on="Hospital_ID",
    how="left"
)

# ============================================
# Merge City Details
# ============================================
master = master.merge(
    cities,
    on=["City", "State"],
    how="left"
)

# ============================================
# Assign One Nurse Per Patient
# ============================================
nurse_map = nurses.groupby("Hospital_ID")["Nurse_ID"].apply(list).to_dict()
nurse_name_map = nurses.set_index("Nurse_ID")["Nurse_Name"].to_dict()

assigned_ids = []
assigned_names = []

for hospital in master["Hospital_ID"]:
    available = nurse_map.get(hospital, [])

    if available:
        nurse = random.choice(available)
        assigned_ids.append(nurse)
        assigned_names.append(nurse_name_map[nurse])
    else:
        assigned_ids.append(None)
        assigned_names.append(None)

master["Nurse_ID"] = assigned_ids
master["Nurse_Name"] = assigned_names
# ============================================
# Validation Checks
# ============================================
print("\nValidation Checks")
print("-" * 40)

print("Shape:", master.shape)
print("\nMissing Values:")
print(master.isnull().sum())

print("\nDuplicate Rows:")
print(master.duplicated().sum())

print("\nMissing Doctor Names:", master["Doctor_Name"].isnull().sum())
print("Missing Hospital Names:", master["Hospital_Name"].isnull().sum())
print("Missing Nurse Names:", master["Nurse_Name"].isnull().sum())
# ============================================
# Format Dates
# ============================================
master["Admission_Date"] = pd.to_datetime(master["Admission_Date"]).dt.strftime("%Y-%m-%d")
master["Discharge_Date"] = pd.to_datetime(master["Discharge_Date"]).dt.strftime("%Y-%m-%d")



# ============================================
# Save Master Dataset
# ============================================
output_file = os.path.join(
    PROCESSED_DIR,
    "medical_operations_master.csv"
)

master.to_csv(output_file, index=False)

# ============================================
# Summary
# ============================================
print("=" * 60)
print("MASTER DATASET CREATED SUCCESSFULLY")
print("=" * 60)

print(f"Rows    : {master.shape[0]}")
print(f"Columns : {master.shape[1]}")

print("\nColumn Names:")
print(master.columns.tolist())

print("\nFirst 5 Rows:")
print(master.head())

print("\nDataset saved to:")
print(output_file)