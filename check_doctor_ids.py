import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

file_path = os.path.join(BASE_DIR, "data", "raw", "Hospital_Operations.csv")

df = pd.read_csv(file_path)

print("First 20 Doctor IDs:")
print(df["Doctor_ID"].head(20))

print("\nUnique Doctor IDs:", df["Doctor_ID"].nunique())