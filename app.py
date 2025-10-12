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
            font-size: 2.3rem;
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
        }
        div[data-testid="stMetric"]:hover {
            box-shadow: 0 0 25px rgba(108, 99, 255, 0.5);
            transform: scale(1.03);
        }
        div[data-testid="stMetricValue"] {
            color: white !important;
            font-size: 30px !important;
            font-weight: bold !important;
        }
        div[data-testid="stMetricLabel"] {
            color: #bbb !important;
            font-size: 14px !important;
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
    # For now, we'll use a simple scoring system
    # In the future, this could use actual distance calculations
    candidate_location = str(candidate.get("Location", "")).lower()
    job_city = str(job.get("City", "")).lower()
    job_state = str(job.get("State", "")).lower()
    
    if job_city in candidate_location or job_state in candidate_location:
        score += 30  # Same city/state
    elif any(state in candidate_location for state in ["ca", "california", "ny", "new york", "tx", "texas"]):
        if job_state in ["ca", "ny", "tx"]:
            score += 20  # Major state match
        else:
            score += 10  # Different state
    else:
        score += 5  # No obvious location match
    
    # 3. Vertical/Industry Alignment (20 points max)
    # This would need candidate preference data in the future
    # For now, give a base score
    job_vertical = str(job.get("Vertical", "")).lower()
    if job_vertical in ["tech", "finance", "life science", "manufacturing"]:
        score += 15  # Common verticals
    else:
        score += 10  # Other verticals
    
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
ready = (df["Readiness"] == "Ready for Placement").sum()
in_progress = (df["Readiness"] == "In Progress").sum()
placed = (df["Readiness"] == "Placed at Training").sum()
new = (df["Readiness"] == "New Start").sum()
open_jobs = len(jobs_df) if not jobs_df.empty else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Candidates", total)
col2.metric("Ready for Placement", ready)
col3.metric("In Progress", in_progress)
col4.metric("Placed at Training", placed)
col5.metric("Open Positions", open_jobs)

# ---- VISUAL SECTION ----
st.markdown("---")
left_col, right_col = st.columns(2)

color_map = {
    "Ready for Placement": "#00CC96",
    "In Progress": "#FECB52",
    "Placed at Training": "#636EFA",
    "New Start": "#AB63FA"
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
    <li><b>{ready}</b> candidate(s) are ready for placement:<br><i>{ready_names or '—'}</i></li>
    <li><b>{in_progress}</b> are actively progressing through training (1–5 weeks):<br><i>{inprog_names or '—'}</i></li>
    <li><b>{placed}</b> have been placed at training sites:<br><i>{placed_names or '—'}</i></li>
    <li><b>{new}</b> are new program starts:<br><i>{newstart_names or '—'}</i></li>
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
st.dataframe(df, use_container_width=True)
st.caption("Data source: combined_mit_data.csv")
