import pandas as pd
import os

# -----------------------------
# File Paths
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_DATA = os.path.join(BASE_DIR, "data", "raw", "Hospital_Operations.csv")

HOSPITALS = os.path.join(BASE_DIR, "data", "reference", "hospitals.csv")
DOCTORS = os.path.join(BASE_DIR, "data", "reference", "doctors.csv")
NURSES = os.path.join(BASE_DIR, "data", "reference", "nurses.csv")
CITIES = os.path.join(BASE_DIR, "data", "reference", "cities.csv")

# -----------------------------
# Load Datasets
# -----------------------------
patients = pd.read_csv(RAW_DATA)
hospitals = pd.read_csv(HOSPITALS)
doctors = pd.read_csv(DOCTORS)
nurses = pd.read_csv(NURSES)
cities = pd.read_csv(CITIES)

# -----------------------------
# Dataset Summary
# -----------------------------
datasets = {
    "Patients": patients,
    "Hospitals": hospitals,
    "Doctors": doctors,
    "Nurses": nurses,
    "Cities": cities
}

for name, df in datasets.items():
    print("=" * 60)
    print(name)
    print("=" * 60)
    print(f"Rows    : {df.shape[0]}")
    print(f"Columns : {df.shape[1]}")

    print("\nColumn Names:")
    print(df.columns.tolist())

    print("\nMissing Values:")
    print(df.isnull().sum())

    print("\nDuplicate Rows:", df.duplicated().sum())

    print("\nFirst 5 Rows:")
    print(df.head())

    print("\n")