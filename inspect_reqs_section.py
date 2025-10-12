import pandas as pd

# --- Load Excel file ---
file_path = "MIT Tracking for Placement(Active_Roster) (1).xlsx"  # adjust name if needed
df_raw = pd.read_excel(file_path, sheet_name=0, header=None)

# --- Find where 'MIT Reqs Open' starts ---
reqs_index = df_raw[df_raw.astype(str).apply(lambda x: x.str.contains("MIT Reqs Open", case=False, na=False)).any(axis=1)].index

if len(reqs_index) == 0:
    print("⚠️ Could not find 'MIT Reqs Open' automatically.")
else:
    reqs_row = reqs_index[0]
    print(f"📍 'MIT Reqs Open' starts at row {reqs_row}")

    # --- Extract headers (row after the label) ---
    headers = df_raw.iloc[reqs_row + 1].tolist()
    print("\n📋 Headers in this section:")
    for h in headers:
        print("-", h)

    # --- Extract data below the headers ---
    df_reqs = df_raw[reqs_row + 2:].copy()
    df_reqs.columns = headers

    # --- Filter rows that have a Start Date ---
    if "Start Date" in df_reqs.columns:
        filtered = df_reqs[df_reqs["Start Date"].notna() & (df_reqs["Start Date"].astype(str).str.strip() != "")]
    else:
        print("\n⚠️ No 'Start Date' column found. Check header names.")
        filtered = df_reqs

    # --- Only show relevant columns (New Candidate Name + Start Date + Status maybe) ---
    keep_cols = [c for c in ["New Candidate Name", "Start Date", "Status"] if c in filtered.columns]
    print("\n🧾 Preview of rows with Start Date:")
    print(filtered[keep_cols].head(10))
