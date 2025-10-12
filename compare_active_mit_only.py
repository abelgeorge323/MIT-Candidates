import pandas as pd
import re
from difflib import SequenceMatcher

# ---------------- CONFIG ----------------
COMBINED_PATH = "combined_mit_data.csv"
EXCEL_PATH = "Copy of 2025 Leadership Development (NLT + MIT) Program Master Roster.xlsx"
ACTIVE_SHEET = "Active Roster"

# ---------------- HELPERS ----------------
def clean_name(name: str) -> str:
    if pd.isna(name):
        return ""
    name = re.sub(r"<[^>]+>", "", str(name))
    name = re.sub(r"[^\w\s]", " ", name.lower())
    return re.sub(r"\s+", " ", name).strip()

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def date_equalish(d1, d2):
    try:
        d1 = pd.to_datetime(d1)
        d2 = pd.to_datetime(d2)
        return d1.date() == d2.date()
    except Exception:
        return False

def site_equalish(s1, s2):
    if pd.isna(s1) or pd.isna(s2):
        return False
    s1, s2 = str(s1).strip().lower(), str(s2).strip().lower()
    return s1 in s2 or s2 in s1

# ---------------- LOAD FILES ----------------
combined = pd.read_csv(COMBINED_PATH)
active = pd.read_excel(EXCEL_PATH, sheet_name=ACTIVE_SHEET)
active.columns = active.columns.str.strip().str.lower()

# Detect key columns
name_col = next((c for c in active.columns if "trainee" in c and "name" in c), None)
program_col = next((c for c in active.columns if "training program" in c), None)
start_col = next((c for c in active.columns if "start" in c and "date" in c), None)
site_col = next((c for c in active.columns if "site" in c), None)

if not all([name_col, program_col]):
    raise ValueError("Missing 'Trainee Name' or 'Training Program' columns in Active Roster.")

# Filter only MIT / SMIT
active_mit = active[active[program_col].astype(str).str.upper().isin(["MIT", "SMIT"])].copy()

# Clean names
combined["CleanName"] = combined["MIT Name"].apply(clean_name)
active_mit["CleanName"] = active_mit[name_col].apply(clean_name)

# ---------------- EXACT MATCH ----------------
combined_names = set(combined["CleanName"])
active_names = set(active_mit["CleanName"])

exact_matches = sorted(combined_names & active_names)
only_in_combined = [n for n in combined_names if n not in active_names]
only_in_active = [n for n in active_names if n not in combined_names]

# ---------------- FUZZY MATCH (DATE + SITE VALIDATION) ----------------
confirmed_fuzzy = []
possible_matches = []

for c_name in only_in_combined:
    c_row = combined[combined["CleanName"] == c_name].iloc[0]
    for a_name in only_in_active:
        score = similarity(c_name, a_name)
        if score >= 0.78:
            a_row = active_mit[active_mit["CleanName"] == a_name].iloc[0]
            c_date = c_row.get("Start date", "")
            a_date = a_row.get(start_col, "")
            c_site = c_row.get("Training Site", "")
            a_site = a_row.get(site_col, "")

            same_date = date_equalish(c_date, a_date)
            same_site = site_equalish(c_site, a_site)
            confirmed = same_date or same_site

            if confirmed:
                confirmed_fuzzy.append((c_name, a_name))
            else:
                possible_matches.append({
                    "Combined Name": c_row["MIT Name"],
                    "Active Name": a_row[name_col],
                    "Similarity": round(score, 3),
                    "Same Start Date": same_date,
                    "Same Site": same_site,
                    "Confirmed Same Person": confirmed,
                    "Combined Start Date": c_date,
                    "Active Start Date": a_date,
                    "Combined Site": c_site,
                    "Active Site": a_site,
                })

# ---------------- MERGE CONFIRMED MATCHES ----------------
# Build a mapping for quick lookup
confirmed_map = dict(confirmed_fuzzy)
exact_map = {n: n for n in exact_matches}
all_matches = {**exact_map, **confirmed_map}

matched_rows = []
for c_name, a_name in all_matches.items():
    c_row = combined[combined["CleanName"] == c_name].iloc[0]
    a_row = active_mit[active_mit["CleanName"] == a_name].iloc[0]
    merged_row = {
        "MIT Name": c_row["MIT Name"],
        "Start date": c_row.get("Start date", ""),
        "Training Site": c_row.get("Training Site", ""),
        "Location": c_row.get("Location", ""),
        "Status": c_row.get("Status", ""),
        "Level": c_row.get("Level", ""),
        "Vert": c_row.get("Vert", ""),
        "Source": c_row.get("Source", ""),
        "Training Program": a_row.get(program_col, ""),
        "Active Start Date": a_row.get(start_col, ""),
        "Active Site": a_row.get(site_col, ""),
    }
    matched_rows.append(merged_row)

merged_df = pd.DataFrame(matched_rows)

# ---------------- OUTPUTS ----------------
merged_df.to_csv("merged_dashboard_ready.csv", index=False)
pd.DataFrame({"Exact Matches": exact_matches}).to_csv("exact_matches.csv", index=False)
pd.DataFrame({"Confirmed Fuzzy": [f"{x[0]} <-> {x[1]}" for x in confirmed_fuzzy]}).to_csv("confirmed_fuzzy.csv", index=False)
pd.DataFrame(possible_matches).to_csv("possible_matches_review.csv", index=False)
pd.DataFrame({"Only in Combined": only_in_combined}).to_csv("only_in_combined.csv", index=False)
pd.DataFrame({"Only in Active": only_in_active}).to_csv("only_in_active.csv", index=False)

# ---------------- SUMMARY ----------------
print("✅ Exact matches:", len(exact_matches))
print("🤝 Confirmed fuzzy matches:", len(confirmed_fuzzy))
print("❌ Only in combined:", len(only_in_combined))
print("⚠️ Only in active:", len(only_in_active))
print(f"🔍 Possible (unconfirmed) fuzzy matches: {len(possible_matches)}")
print("\n📁 Outputs created:")
print(" - merged_dashboard_ready.csv (for dashboard)")
print(" - exact_matches.csv")
print(" - confirmed_fuzzy.csv")
print(" - possible_matches_review.csv (manual check)")
print(" - only_in_combined.csv")
print(" - only_in_active.csv")
