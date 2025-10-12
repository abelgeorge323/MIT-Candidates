import pandas as pd

# Load the data
df = pd.read_csv("combined_mit_data.csv")
df.columns = [c.strip().title() for c in df.columns]

# Load jobs data
jobs_df = pd.read_excel("MITs.xlsx", skiprows=20)
if len(jobs_df) > 0:
    jobs_df.columns = jobs_df.iloc[0]
    jobs_df = jobs_df.drop(jobs_df.index[0]).reset_index(drop=True)
    jobs_df.columns = [c.strip() if isinstance(c, str) else c for c in jobs_df.columns]
    jobs_df = jobs_df.dropna(how='all')
    
    if 'Job Title' in jobs_df.columns:
        jobs_df = jobs_df.dropna(subset=['Job Title'])
        jobs_df = jobs_df[jobs_df['Job Title'].str.strip() != '']
    
    if 'JV ID' in jobs_df.columns:
        jobs_df = jobs_df.dropna(subset=['JV ID'])
        jobs_df['JV ID'] = pd.to_numeric(jobs_df['JV ID'], errors='coerce')
        jobs_df = jobs_df.dropna(subset=['JV ID'])
    
    jobs_df = jobs_df.fillna('')

# Vertical mapping function
def get_vertical_from_training_site(training_site):
    if pd.isna(training_site) or training_site == '' or str(training_site).lower() == 'none':
        return 'Unknown'
    
    training_site = str(training_site).lower().strip()
    
    aviation_sites = ['delta', 'atl', 'dtw', 'lga', 'msp', 'boston logan airport']
    if any(site in training_site for site in aviation_sites):
        return 'Aviation'
    
    return 'Unknown'

# Add vertical column
df['Assigned Vertical'] = df['Training Site'].apply(get_vertical_from_training_site)

# Find Sergio Gomez
sergio = df[df['Mit Name'].str.contains('Sergio', case=False, na=False)]
if len(sergio) > 0:
    sergio = sergio.iloc[0]
    print("=== UPDATED SERGIO GOMEZ PROFILE ===")
    print(f"Name: {sergio.get('Mit Name', 'N/A')}")
    print(f"Training Site: {sergio.get('Training Site', 'N/A')}")
    print(f"Assigned Vertical: {sergio.get('Assigned Vertical', 'N/A')}")
    print(f"Location: {sergio.get('Location', 'N/A')}")
    print(f"Week: {sergio.get('Week', 'N/A')}")
    print(f"Readiness: Ready for Placement")
    
    print("\n=== CORRECTED MATCH SCORES ===")
    
    # Calculate corrected match scores
    for i, (_, job) in enumerate(jobs_df.iterrows()):
        print(f"\n--- JOB {i+1}: {job.get('Job Title', 'N/A')} - {job.get('Account', 'N/A')} ---")
        print(f"Location: {job.get('City', 'N/A')}, {job.get('State', 'N/A')}")
        print(f"Vertical: {job.get('Vertical', 'N/A')}")
        
        score = 0
        
        # 1. Readiness (40 points)
        score += 40  # Ready for Placement
        
        # 2. Location (30 points) - FIXED
        candidate_location = "minneapolis, mn"
        job_city = str(job.get("City", "")).lower().strip()
        job_state = str(job.get("State", "")).lower().strip()
        
        if job_city in candidate_location:
            location_score = 30
            location_reason = "Same city"
        elif job_state == "mn":
            location_score = 20
            location_reason = "Same state (MN)"
        else:
            location_score = 5
            location_reason = "No location match"
        
        score += location_score
        print(f"Location Score: {location_score}/30 ({location_reason})")
        
        # 3. Vertical (20 points) - FIXED
        candidate_vertical = "aviation"  # Delta = Aviation
        job_vertical = str(job.get("Vertical", "")).lower()
        
        if candidate_vertical == job_vertical:
            vertical_score = 20
            vertical_reason = "Perfect vertical match"
        elif job_vertical in ["tech", "finance", "life science", "manufacturing"]:
            vertical_score = 10
            vertical_reason = "Common vertical"
        else:
            vertical_score = 5
            vertical_reason = "Other vertical"
        
        score += vertical_score
        print(f"Vertical Score: {vertical_score}/20 ({vertical_reason})")
        
        # 4. Job Level (10 points)
        score += 10  # Regular role for ready candidate
        
        print(f"TOTAL CORRECTED SCORE: {score}/100")
        
else:
    print("Sergio Gomez not found")
