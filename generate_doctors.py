import pandas as pd
import random
import os

# -----------------------------
# Project Paths
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REFERENCE_DIR = os.path.join(BASE_DIR, "data", "reference")
OUTPUT_FILE = os.path.join(REFERENCE_DIR, "doctors.csv")

# -----------------------------
# Hospital IDs
# -----------------------------
hospital_ids = [f"H{str(i).zfill(3)}" for i in range(1, 26)]

# -----------------------------
# Departments
# -----------------------------
departments = [
    "Cardiology",
    "Neurology",
    "Orthopedics",
    "Emergency",
    "Pediatrics",
    "Gynecology",
    "Oncology",
    "Dermatology",
    "General Medicine",
    "ENT"
]

# -----------------------------
# Indian First Names
# -----------------------------
first_names = [
    "Aarav","Vivaan","Aditya","Arjun","Krishna","Rahul","Rohan","Karan",
    "Priya","Sneha","Anjali","Pooja","Neha","Kavya","Shreya","Meera",
    "Amit","Vikas","Deepak","Suresh","Raj","Nikhil","Akash","Varun",
    "Ritu","Komal","Nisha","Divya","Swati","Aisha"
]

# -----------------------------
# Last Names
# -----------------------------
last_names = [
    "Sharma","Verma","Singh","Patel","Kumar","Gupta","Reddy","Iyer",
    "Sinha","Mishra","Yadav","Das","Joshi","Roy","Chopra","Malhotra",
    "Kapoor","Nair","Menon","Bose"
]

# -----------------------------
# Generate Doctors
# -----------------------------
records = []

for i in range(1, 501):

    doctor_id = f"DOC{str(i).zfill(4)}"

    doctor_name = (
        "Dr. "
        + random.choice(first_names)
        + " "
        + random.choice(last_names)
    )

    department = random.choice(departments)

    hospital_id = random.choice(hospital_ids)

    records.append([
        doctor_id,
        doctor_name,
        department,
        hospital_id
    ])

# -----------------------------
# Create DataFrame
# -----------------------------
doctors = pd.DataFrame(
    records,
    columns=[
        "Doctor_ID",
        "Doctor_Name",
        "Department",
        "Hospital_ID"
    ]
)

# -----------------------------
# Save CSV
# -----------------------------
doctors.to_csv(OUTPUT_FILE, index=False)

print("=" * 60)
print("Doctors dataset created successfully!")
print("=" * 60)
print("Rows :", doctors.shape[0])
print("Columns :", doctors.shape[1])
print("\nSaved to:")
print(OUTPUT_FILE)

print("\nFirst 5 Records:\n")
print(doctors.head())