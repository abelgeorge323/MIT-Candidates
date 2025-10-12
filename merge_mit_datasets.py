import pandas as pd

# === STEP 1: Load both CSVs ===
roster = pd.read_csv("active_roster_unplaced.csv")
offers = pd.read_csv("offer_accepted_candidates.csv")

# === STEP 2: Clean & normalize columns ===
# Clean headers
roster.columns = [c.strip() for c in roster.columns]
offers.columns = [c.strip().lower().replace(" ", "_") for c in offers.columns]

# Drop irrelevant column (like 'jv')
if "jv" in offers.columns:
    offers.drop(columns=["jv"], inplace=True)

# Rename columns in offers to match roster
offers = offers.rename(columns={
    "new_candidate_name": "MIT Name",
    "start_date": "Start date",
    "training_site": "Training Site",
    "location": "Location",
    "level": "Level"
})

# Add missing fields in both datasets
for col in ["Week", "Status", "Level", "Vert", "Source"]:
    if col not in roster.columns:
        roster[col] = "N/A"
    if col not in offers.columns:
        offers[col] = "N/A"

# Normalize fields
roster["Source"] = "Active Roster"
offers["Week"] = 0
offers["Status"] = "Offer Accepted"
offers["Vert"] = "N/A"
offers["Source"] = "Offer Accepted"

# Reorder columns
columns = ["MIT Name", "Week", "Start date", "Training Site", "Location", "Status", "Level", "Vert", "Source"]
roster = roster[columns]
offers = offers[columns]

# === STEP 3: Merge datasets ===
combined = pd.concat([roster, offers], ignore_index=True)

# === STEP 4: Save result ===
combined.to_csv("combined_mit_data.csv", index=False)

print("✅ Combined file created successfully: combined_mit_data.csv")
print(f"📊 Total rows: {len(combined)}")
print("🔍 Preview:")
print(combined.head(10))

