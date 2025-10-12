import pandas as pd

# --- Step 1: Load your Excel file ---
file_path = "MIT Tracking for Placement(Active_Roster) (1).xlsx"  # match your exact file name

# Load the first sheet (0 = first sheet)
df_raw = pd.read_excel(file_path, sheet_name=0, header=None)

# --- Step 2: Extract headers from the second row (row index 1) ---
headers = df_raw.iloc[1].tolist()

# --- Step 3: Print them ---
print("\n📋 Column Names Found in Excel:")
for h in headers:
    print("-", h)
