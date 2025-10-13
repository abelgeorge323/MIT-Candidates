import pandas as pd
import streamlit as st
import plotly.express as px

# ---- PAGE CONFIG ----
st.set_page_config(page_title="MIT Candidate Training Dashboard", layout="wide")

# ---- CUSTOM STYLING ----
st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] {
            background-color: #0E1117;
            color: white;
        }
        .dashboard-title {
            font-size: clamp(1.6rem, 3.2vw, 2.3rem);
            font-weight: 700;
            color: white;
            background: linear-gradient(90deg, #6C63FF, #00B4DB);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        div[data-testid="stMetric"] {
            background: #1E1E1E;
            border-radius: 15px;
            padding: 20px 25px;
            box-shadow: 0 0 12px rgba(108, 99, 255, 0.25);
            border-left: 6px solid #6C63FF;
            transition: 0.3s ease;
            min-width: 220px;
        }
        div[data-testid="stMetric"]:hover {
            box-shadow: 0 0 25px rgba(108, 99, 255, 0.5);
            transform: scale(1.03);
        }
        div[data-testid="stMetricValue"] {
            color: white !important;
            font-size: clamp(22px, 2.2vw, 30px) !important;
            font-weight: bold !important;
        }
        div[data-testid="stMetricLabel"] {
            color: #E5E7EB !important; /* ensure light text on dark bg */
            font-size: clamp(12px, 1.2vw, 14px) !important;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        div[data-testid="stMetricLabel"] * { color: #E5E7EB !important; }
        div[data-testid="stMetricValue"] * { color: #FFFFFF !important; }
        /* Help icon inside metrics */
        div[data-testid="stMetric"] svg path { fill: #E5E7EB !important; }
        @media (max-width: 1400px) {
            div[data-testid="stMetric"] { min-width: 200px; padding: 18px 20px; }
        }
        @media (max-width: 1100px) {
            div[data-testid="stMetric"] { min-width: 170px; padding: 16px 18px; }
        }
        h3, h4 {
            color: white !important;
            font-weight: 600;
        }
        .insights-box {
            background: #1E1E1E;
            border-radius: 12px;
            padding: 20px;
            margin-top: 15px;
            box-shadow: 0 0 10px rgba(108, 99, 255, 0.15);
        }
        .placeholder-box {
            background: #1E1E1E;
            border-radius: 12px;
            padding: 80px;
            text-align: center;
            font-size: 1.2rem;
            color: #bbb;
            box-shadow: 0 0 10px rgba(108, 99, 255, 0.1);
        }
    </style>
""", unsafe_allow_html=True)

# ---- LOAD DATA ----
@st.cache_data
def load_data():
    df = pd.read_csv("combined_mit_data.csv")
    df.columns = [c.strip().title() for c in df.columns]

    if "Week" in df.columns:
        df["Week"] = pd.to_numeric(df["Week"], errors="coerce").fillna(0).astype(int)

    if "Start Date" in df.columns:
        df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce").dt.strftime("%m/%d/%Y")

    def infer_readiness(row):
        w = row.get("Week", 0)
        status = str(row.get("Status", "")).lower()
        src = str(row.get("Source", "")).lower()

        if "offer accepted" in status or "placed" in src:
            return "Placed at Training"
        elif w >= 6:
            return "Ready for Placement"
        elif 1 <= w < 6:
            return "In Progress"
        else:
            return "New Start"

    df["Readiness"] = df.apply(infer_readiness, axis=1)
    return df

@st.cache_data
def load_jobs_data():
    """Load open job positions from Excel file"""
    try:
        # Read the Excel file, starting from row 21 (index 20)
        jobs_df = pd.read_excel("MITs.xlsx", skiprows=20)
        
        # Clean up the data - first row contains headers
        if len(jobs_df) > 0:
            # Use first row as column names
            jobs_df.columns = jobs_df.iloc[0]
            jobs_df = jobs_df.drop(jobs_df.index[0]).reset_index(drop=True)
            
            # Clean column names
            jobs_df.columns = [c.strip() if isinstance(c, str) else c for c in jobs_df.columns]
            
            # Remove any completely empty rows
            jobs_df = jobs_df.dropna(how='all')
            
            # Remove rows where Job Title is empty or NaN
            if 'Job Title' in jobs_df.columns:
                jobs_df = jobs_df.dropna(subset=['Job Title'])
                jobs_df = jobs_df[jobs_df['Job Title'].str.strip() != '']
            
            # Only keep rows that have valid JV ID (to filter out header rows and invalid data)
            if 'JV ID' in jobs_df.columns:
                jobs_df = jobs_df.dropna(subset=['JV ID'])
                # Convert JV ID to numeric and keep only valid numbers
                jobs_df['JV ID'] = pd.to_numeric(jobs_df['JV ID'], errors='coerce')
                jobs_df = jobs_df.dropna(subset=['JV ID'])
            
            # Fill NaN values with empty strings for display
            jobs_df = jobs_df.fillna('')
            
        return jobs_df
    except Exception as e:
        st.error(f"Error loading jobs data: {e}")
        return pd.DataFrame()

df = load_data()
jobs_df = load_jobs_data()

# ---- VERTICAL MAPPING FUNCTION ----
def get_vertical_from_training_site(training_site):
    """
    Map training sites to their corresponding verticals based on the provided mapping
    """
    if pd.isna(training_site) or training_site == '' or str(training_site).lower() == 'none':
        return 'Unknown'
    
    training_site = str(training_site).lower().strip()
    
    # Aviation
    aviation_sites = ['delta', 'atl', 'dtw', 'lga', 'msp', 'boston logan airport']
    if any(site in training_site for site in aviation_sites):
        return 'Aviation'
    
    # Automotive
    automotive_sites = ['ford', 'gm', 'tesla', 'honda', 'stellantis', 'leadec', 'ddc']
    if any(site in training_site for site in automotive_sites):
        return 'Automotive'
    
    # Distribution
    distribution_sites = ['nike', 'p&g', 'procter & gamble']
    if any(site in training_site for site in distribution_sites):
        return 'Distribution'
    
    # Finance
    finance_sites = ['wells fargo', 'state farm', 'fidelity', 'charles schwab', 't. rowe price', 
                    'usaa', 'chubb', 'metlife', 'deutsche bank', 'cigna', 'elevance']
    if any(site in training_site for site in finance_sites):
        return 'Finance'
    
    # Manufacturing
    manufacturing_sites = ['boeing', 'ge aerospace', '3m', 'ball corporation', 'dupont', 
                          'westinghouse', 'lockheed martin', 'general dynamics', 'northrop grumman', 
                          'textron']
    if any(site in training_site for site in manufacturing_sites):
        return 'Manufacturing'
    
    # Technology
    tech_sites = ['google', 'uber', 'adobe', 'meta', 'microsoft', 'nvidia', 'juniper', 'amd', 
                 'irg', 'snap', 'computershare', 'stripe', 'tgs mgmt', 'cpi satcom', 'softlayer', 
                 'ntt', 'google fiber', 'google data centers', 'scale ai', 'hp', 'xerox', 
                 'lam research', 'photronix', 'siltronics', 'intel', 'micron']
    if any(site in training_site for site in tech_sites):
        return 'Technology'
    
    # Life Science
    life_science_sites = ['abbott', 'atara bio', 'capsida', 'medtronic', 'bio-rad', 'eli lilly', 
                         'amgen', 'elanco', 'gilead', 'kite', 'avid bio', 'merck', 'cbre', 
                         'bms', 'bristol myers squibb', 'novartis', 'abbvie', 'millipore sigma', 
                         'bayer', 'johnson & johnson', 'biogen', 'genentech', 'lonza biologics', 
                         'boehringer ingelheim', 'sanofi', 'takeda']
    if any(site in training_site for site in life_science_sites):
        return 'Life Science'
    
    # R&D / Education / Other
    rd_sites = ['mars', 'ge healthcare', 'nestle']
    if any(site in training_site for site in rd_sites):
        return 'R&D / Education / Other'
    
    return 'Unknown'

# Add vertical column to the dataframe
df['Assigned Vertical'] = df['Training Site'].apply(get_vertical_from_training_site)

# ---- MATCH SCORE ALGORITHM ----
def calculate_match_score(candidate, job):
    """
    Calculate match score between candidate and job position
    Returns score from 0-100
    """
    score = 0
    max_score = 100
    
    # 1. Candidate Readiness (40 points max)
    readiness = candidate.get("Readiness", "")
    if readiness == "Ready for Placement":
        score += 40
    elif readiness == "In Progress":
        # Partial score based on weeks completed
        weeks = candidate.get("Week", 0)
        if weeks >= 4:
            score += 30
        elif weeks >= 2:
            score += 20
        else:
            score += 10
    elif readiness == "Placed at Training":
        score += 0  # Already placed
    else:  # New Start
        score += 5
    
    # 2. Location Proximity (30 points max)
    # Improved location matching with better accuracy
    candidate_location = str(candidate.get("Location", "")).lower().strip()
    job_city = str(job.get("City", "")).lower().strip()
    job_state = str(job.get("State", "")).lower().strip()
    
    # Extract state from candidate location
    candidate_state = ""
    if "," in candidate_location:
        candidate_state = candidate_location.split(",")[-1].strip()
    
    # Exact city match
    if job_city in candidate_location:
        score += 30  # Same city
    # Same state match
    elif job_state == candidate_state and candidate_state != "":
        score += 20  # Same state
    # Major state proximity (within region)
    elif any(state in candidate_location for state in ["ca", "california", "ny", "new york", "tx", "texas", "il", "illinois", "mn", "minnesota"]):
        if job_state in ["ca", "ny", "tx", "il", "mn"]:
            score += 15  # Major state match
        else:
            score += 8  # Different major state
    else:
        score += 5  # No obvious location match
    
    # 3. Vertical/Industry Alignment (20 points max)
    # Use the assigned vertical from training site mapping
    candidate_vertical = str(candidate.get("Assigned Vertical", "")).lower()
    job_vertical = str(job.get("Vertical", "")).lower()
    
    # Perfect vertical match
    if candidate_vertical == job_vertical and candidate_vertical != "unknown":
        score += 20  # Perfect match
    # Related verticals (e.g., Technology and some Manufacturing)
    elif (candidate_vertical == "technology" and job_vertical in ["tech", "manufacturing"]) or \
         (candidate_vertical == "manufacturing" and job_vertical in ["tech", "manufacturing"]) or \
         (candidate_vertical == "life science" and job_vertical in ["life science", "manufacturing"]) or \
         (candidate_vertical == "finance" and job_vertical in ["finance", "tech"]):
        score += 15  # Related verticals
    # Common verticals get base score
    elif job_vertical in ["tech", "finance", "life science", "manufacturing"]:
        score += 10  # Common verticals
    else:
        score += 5   # Other verticals
    
    # 4. Job Level Match (10 points max)
    candidate_weeks = candidate.get("Week", 0)
    job_title = str(job.get("Job Title", "")).lower()
    
    if "sr." in job_title or "senior" in job_title:
        if candidate_weeks >= 8:
            score += 10  # Senior role for experienced candidate
        else:
            score += 5   # Senior role for less experienced
    else:
        if candidate_weeks >= 6:
            score += 10  # Regular role for ready candidate
        else:
            score += 7   # Regular role for developing candidate
    
    return min(score, max_score)

def get_candidate_match_scores(candidates_df, jobs_df):
    """
    Calculate match scores for all candidates against all jobs
    """
    match_scores = []
    
    for _, candidate in candidates_df.iterrows():
        candidate_scores = []
        for _, job in jobs_df.iterrows():
            score = calculate_match_score(candidate, job)
            candidate_scores.append({
                'Job': f"{job.get('Job Title', 'N/A')} - {job.get('Account', 'N/A')}",
                'Location': f"{job.get('City', 'N/A')}, {job.get('State', 'N/A')}",
                'Vertical': job.get('Vertical', 'N/A'),
                'Match Score': score
            })
        
        # Sort by match score (highest first)
        candidate_scores.sort(key=lambda x: x['Match Score'], reverse=True)
        match_scores.append({
            'Candidate': candidate.get('Mit Name', 'Unknown'),
            'Readiness': candidate.get('Readiness', 'Unknown'),
            'Week': candidate.get('Week', 0),
            'Top Matches': candidate_scores[:3]  # Top 3 matches
        })
    
    return match_scores

# ---- DASHBOARD HEADER ----
st.markdown('<div class="dashboard-title">🎓 MIT Candidate Training Dashboard</div>', unsafe_allow_html=True)

# ---- KEY METRICS ----
total = len(df)

# Buckets per your definitions
ready = (df["Readiness"] == "Ready for Placement").sum()
in_training = (df["Readiness"] == "In Progress").sum()  # Weeks 1–5
placed_training = (df["Readiness"] == "Placed at Training").sum()
new_starts = (df["Readiness"] == "New Start").sum()
started_mit_training = int(placed_training + new_starts)  # grouped bucket

open_jobs = len(jobs_df) if not jobs_df.empty else 0

col1, col2, col3, col4, col5 = st.columns(5)

# Executive-facing order: Total → Open Positions → Ready → In Training → Started
col1.metric(
    "Total Candidates",
    total,
    help="All candidates currently in the MIT program dataset"
)
col2.metric(
    "Open Positions",
    open_jobs,
    help="Number of active openings available to place candidates"
)
col3.metric(
    "Ready for Placement",
    ready,
    help="Candidates at Week ≥ 6 who are not already placed"
)
col4.metric(
    "In Training (Weeks 1–5)",
    in_training,
    help="Candidates actively progressing through Weeks 1–5 of training"
)
col5.metric(
    "Started MIT Training",
    started_mit_training,
    help="New Program Starts (Week 0) plus those placed at training sites"
)

# ---- VISUAL SECTION ----
st.markdown("---")
left_col, right_col = st.columns([1.05, 0.95])

# High-contrast, colorblind-friendly palette
color_map = {
    "Ready for Placement": "#2E91E5",  # blue
    "In Progress": "#E15F99",         # magenta
    "Placed at Training": "#1CA71C",   # green
    "New Start": "#FB0D0D"            # red
}

# Left side: open job positions
with left_col:
    st.subheader("📍 Open Job Positions")
    if not jobs_df.empty:
        # Create a cleaner display of job positions
        display_jobs = jobs_df.copy()
        
        # Create a more concise summary column
        if 'Job Title' in display_jobs.columns and 'Account' in display_jobs.columns and 'City' in display_jobs.columns and 'State' in display_jobs.columns:
            display_jobs['Position'] = display_jobs.apply(
                lambda row: f"{row.get('Job Title', 'N/A')} - {row.get('Account', 'N/A')}", 
                axis=1
            )
            display_jobs['Location'] = display_jobs.apply(
                lambda row: f"{row.get('City', 'N/A')}, {row.get('State', 'N/A')}", 
                axis=1
            )
            
            # Show clean columns
            clean_columns = ['Position', 'Location', 'Vertical', 'Notes']
            available_columns = [col for col in clean_columns if col in display_jobs.columns]
            
            if available_columns:
                # Style the dataframe for better readability
                styled_df = display_jobs[available_columns].copy()
                st.dataframe(
                    styled_df, 
                    use_container_width=True,
                    height=450,
                    hide_index=True
                )
            else:
                st.dataframe(display_jobs, use_container_width=True, height=450)
        else:
            st.dataframe(display_jobs, use_container_width=True, height=450)
    else:
        st.markdown('<div class="placeholder-box">No job positions data available</div>', unsafe_allow_html=True)

# Right side: pie chart
with right_col:
    st.subheader("📊 Candidate Readiness Mix")
    readiness_counts = df["Readiness"].value_counts().reset_index()
    readiness_counts.columns = ["Readiness", "Count"]

    fig_pie = px.pie(
        readiness_counts,
        names="Readiness",
        values="Count",
        hole=0.45,
        color="Readiness",
        color_discrete_map=color_map
    )
    fig_pie.update_layout(
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font_color="white",
        height=480,  # slightly larger
        margin=dict(l=0, r=0, t=30, b=30),
        showlegend=True,
    )
    # Improve readability across devices
    fig_pie.update_traces(
        textposition="inside",
        textinfo="percent+label",
        textfont=dict(color="#FFFFFF", size=14),
        marker=dict(line=dict(color="#0B0F14", width=2))
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# ---- QUICK INSIGHTS ----
# ---- QUICK INSIGHTS ----
st.markdown("<h3>🧠 Quick Insights</h3>", unsafe_allow_html=True)

# Helper to list names by readiness category
def get_names(stage):
    # Column is "Mit Name" because you title-cased headers earlier
    return ", ".join(df.loc[df["Readiness"] == stage, "Mit Name"].dropna().tolist())

ready_names    = get_names("Ready for Placement")
inprog_names   = get_names("In Progress")
placed_names   = get_names("Placed at Training")
newstart_names = get_names("New Start")

st.markdown(f"""
<div class="insights-box">
<ul>
    <li><b>{ready}</b> Ready for Placement (Week ≥ 6):<br><i>{ready_names or '—'}</i></li>
    <li><b>{in_training}</b> In Training (Weeks 1–5):<br><i>{inprog_names or '—'}</i></li>
    <li><b>{started_mit_training}</b> Started MIT Training (New Starts + Placed at Site)</li>
    <ul>
        <li><b>{new_starts}</b> New Program Starts:<br><i>{newstart_names or '—'}</i></li>
        <li><b>{placed_training}</b> Placed at Training Sites:<br><i>{placed_names or '—'}</i></li>
    </ul>
</ul>
</div>
""", unsafe_allow_html=True)



# ---- CANDIDATE-JOB MATCHING SECTION ----
st.markdown("---")
st.markdown("### 🎯 Candidate-Job Matching")

if not jobs_df.empty and ready > 0:
    # Get ready candidates
    ready_candidates = df[df["Readiness"] == "Ready for Placement"]
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("👥 Ready Candidates")
        if not ready_candidates.empty:
            candidate_display = ready_candidates[['Mit Name', 'Week', 'Start Date']].copy() if 'Mit Name' in ready_candidates.columns else ready_candidates
            st.dataframe(candidate_display, use_container_width=True, height=300)
        else:
            st.info("No candidates ready for placement")
    
    with col2:
        st.subheader("💼 Available Positions")
        if 'Job Title' in jobs_df.columns and 'Account' in jobs_df.columns:
            position_display = jobs_df[['Job Title', 'Account', 'City', 'State', 'Vertical']].copy()
            # Remove empty rows
            position_display = position_display.dropna(how='all')
            st.dataframe(position_display, use_container_width=True, height=300)
        else:
            st.dataframe(jobs_df, use_container_width=True, height=300)
    
    # Matching suggestions
    st.subheader("💡 Matching Suggestions")
    st.info(f"""
    **Quick Match Summary:**
    - {ready} candidates are ready for placement
    - {open_jobs} open positions available
    
    **Next Steps:**
    1. Review candidate profiles and preferences
    2. Consider location preferences and vertical experience
    3. Match based on skills and career goals
    4. Coordinate interviews and placement process
    """)
    
else:
    if ready == 0:
        st.info("No candidates are currently ready for placement. Check back when candidates reach 6+ weeks of training.")
    if jobs_df.empty:
        st.warning("No job positions data available. Please ensure MITs.xlsx is properly formatted.")

# ---- CANDIDATE MATCH SCORES SECTION ----
st.markdown("---")
st.markdown("### 🎯 Candidate Match Scores")

if not jobs_df.empty and len(df) > 0:
    # Calculate match scores
    match_scores = get_candidate_match_scores(df, jobs_df)
    
    # Display match scores for each candidate
    for candidate_data in match_scores:
        with st.expander(f"👤 {candidate_data['Candidate']} - {candidate_data['Readiness']} (Week {candidate_data['Week']})"):
            st.write("**Top 3 Job Matches:**")
            
            for i, match in enumerate(candidate_data['Top Matches'], 1):
                # Color code the match score
                score = match['Match Score']
                if score >= 80:
                    color = "🟢"
                elif score >= 60:
                    color = "🟡"
                else:
                    color = "🔴"
                
                st.write(f"{i}. {color} **{match['Job']}**")
                st.write(f"   📍 {match['Location']} | 🏢 {match['Vertical']} | ⭐ Match Score: {score}/100")
                st.write("")
else:
    st.info("No data available for match score calculation.")

# ---- DATA TABLE ----
st.markdown("---")
st.markdown("### 📋 Full Combined Roster")

# Create a display dataframe with key columns including the new vertical
display_columns = ['Mit Name', 'Week', 'Start Date', 'Training Site', 'Location', 'Status', 'Assigned Vertical', 'Readiness']
available_columns = [col for col in display_columns if col in df.columns]

if available_columns:
    st.dataframe(df[available_columns], use_container_width=True)
else:
    st.dataframe(df, use_container_width=True)

st.caption("Data source: combined_mit_data.csv | Verticals assigned based on training site mapping")
