import pandas as pd

file_path = "MIT Tracking for Placement(Active_Roster) (1).xlsx"
df_raw = pd.read_excel(file_path, sheet_name=0, header=None)

# --- Locate the 'MIT Reqs Open' section ---
reqs_index = df_raw[df_raw.astype(str).apply(lambda x: x.str.contains("MIT Reqs Open", case=False, na=False)).any(axis=1)].index

if len(reqs_index) == 0:
    print("⚠️ 'MIT Reqs Open' section not found.")
    exit()

reqs_row = reqs_index[0]
print(f"📍 Found 'MIT Reqs Open' starting at row {reqs_row}")

# --- Extract headers and data ---
headers = df_raw.iloc[reqs_row + 1].tolist()
headers = [str(h).strip().replace('\xa0', ' ') for h in headers]  # clean weird spaces
df_reqs = df_raw[reqs_row + 2:].copy()
df_reqs.columns = headers

print("\n🧩 Cleaned Headers Detected:")
print(df_reqs.columns.tolist())

# --- Normalize column names to avoid mismatches ---
def normalize(col):
    return col.strip().lower().replace(' ', ' ')  # normalize invisible spaces

norm_cols = {col: normalize(col) for col in df_reqs.columns}
df_reqs.rename(columns=norm_cols, inplace=True)

# --- Identify likely 'start date' column ---
possible_date_cols = [c for c in df_reqs.columns if "start" in c and "date" in c]
start_col = possible_date_cols[0] if possible_date_cols else None

if not start_col:
    print("⚠️ Could not detect 'Start Date' column automatically.")
else:
    print(f"✅ Using '{start_col}' as Start Date column.")

# --- Filter for Offer Accepted ---
offer_df = df_reqs[df_reqs["status"].astype(str).str.strip().eq("Offer Accepted")]

# --- Select only relevant columns (use normalized names) ---
keep_cols = ["jv", "new candidate name", start_col, "training site", "location", "level"]
keep_cols = [c for c in keep_cols if c in offer_df.columns]

filtered = offer_df[keep_cols]

# --- Save ---
filtered.to_csv("offer_accepted_candidates.csv", index=False)

print("\n✅ Saved offer_accepted_candidates.csv")
print("🔍 Preview:")
print(filtered.head(10))
