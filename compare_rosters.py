import pandas as pd

# ==== Load files ====
combined_path = "combined_mit_data.csv"
excel_path = "Copy of 2025 Leadership Development (NLT + MIT) Program Master Roster.xlsx"

# Read combined CSV
combined_df = pd.read_csv(combined_path)
combined_df["MIT Name"] = combined_df["MIT Name"].str.strip().str.lower()

# Read Excel file sheets
xl = pd.ExcelFile(excel_path)
active = xl.parse("Active Roster")
graduated = xl.parse("Graduated Roster")

# Normalize column names
active.columns = active.columns.str.strip().str.lower()
graduated.columns = graduated.columns.str.strip().str.lower()

# Filter only MIT / SMIT programs
def filter_mit(df):
    if "training program" in df.columns:
        df = df[df["training program"].astype(str).str.upper().isin(["MIT", "SMIT"])]
    return df

active_mit = filter_mit(active)
graduated_mit = filter_mit(graduated)

# Extract trainee names
def clean_names(df, col_name="trainee name"):
    return df[col_name].dropna().str.strip().str.lower().tolist()

active_names = clean_names(active_mit)
grad_names = clean_names(graduated_mit)
all_excel_names = set(active_names + grad_names)

# Compare to combined CSV names
combined_names = set(combined_df["MIT Name"].dropna().str.lower())

matched = combined_names.intersection(all_excel_names)
missing_in_excel = combined_names - all_excel_names
missing_in_combined = all_excel_names - combined_names

# ==== Output results ====
print("✅ MATCHED NAMES:")
for n in sorted(matched):
    print(" -", n.title())

print("\n❌ In Combined CSV but NOT in Excel:")
for n in sorted(missing_in_excel):
    print(" -", n.title())

print("\n⚠️ In Excel but NOT in Combined CSV:")
for n in sorted(missing_in_combined):
    print(" -", n.title())

# Optional: save results
summary = pd.DataFrame({
    "Matched": sorted(matched),
    "Only in Combined CSV": sorted(missing_in_excel),
    "Only in Excel": sorted(missing_in_combined)
})
summary.to_csv("name_comparison_summary.csv", index=False)
print("\n📁 Saved detailed comparison to name_comparison_summary.csv")
