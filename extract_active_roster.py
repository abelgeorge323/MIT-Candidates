import pandas as pd

# === Load Excel file ===
file_path = "MIT Tracking for Placement(Active_Roster) (1).xlsx"  # adjust if needed
df_raw = pd.read_excel(file_path, sheet_name=0, header=None)

# === Find where "MIT Reqs Open" starts ===
reqs_index = df_raw[df_raw.astype(str).apply(lambda x: x.str.contains("MIT Reqs Open", case=False, na=False)).any(axis=1)].index

# If found, cut the top section up to that row
if len(reqs_index) == 0:
    end_row = len(df_raw)
    print("⚠️ 'MIT Reqs Open' not found. Reading entire file as top section.")
else:
    end_row = reqs_index[0]
    print(f"📍 Top section ends before row {end_row}")

# === Extract headers and top section ===
headers = df_raw.iloc[1].tolist()
top_df = df_raw[2:end_row].copy()
top_df.columns = headers

# === Filter logic: only rows where Status does NOT contain "placed" ===
if "Status" not in top_df.columns:
    print("⚠️ Could not find 'Status' column. Found columns instead:")
    print(top_df.columns.tolist())
    exit()

mask = ~top_df["Status"].astype(str).str.lower().str.contains("place", na=False)
filtered_top = top_df[mask]

# === Select only the relevant columns ===
columns_to_keep = ["MIT Name", "Week", "Start date", "Training Site", "Location"]
columns_present = [c for c in columns_to_keep if c in filtered_top.columns]
filtered_top = filtered_top[columns_present]

# === Drop empty names ===
filtered_top = filtered_top.dropna(subset=["MIT Name"])

# === Save to CSV ===
filtered_top.to_csv("active_roster_unplaced.csv", index=False)

# === Print preview ===
print("\n✅ Saved active_roster_unplaced.csv")
print("🔍 Preview:")
print(filtered_top.head(10))
