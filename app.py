import pandas as pd
import streamlit as st
import plotly.express as px

# ---- PAGE CONFIG (must come FIRST) ----
st.set_page_config(
    page_title="MIT Candidate Training Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---- FORCE DARK MODE ACROSS ALL BROWSERS ----
# This locks dark theme even if Streamlit user/browser has light mode set
st.markdown("""
<style>
/* ===== Force Global Dark Mode ===== */
:root,
html[data-theme="light"],
html[data-theme="dark"] {
    color-scheme: dark !important;
    --background-color: #0e1016 !important;
    --text-color: #e0e0e0 !important;
    --secondary-bg-color: #151820 !important;
    --primary-color: #4aa8e0 !important;
}

/* App Containers */
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] {
    background-color: var(--background-color) !important;
    color: var(--text-color) !important;
}

/* Metrics, Tables, Expanders, Charts */
[data-testid="stMetric"],
[data-testid="stDataFrame"],
[data-testid="stExpander"],
[data-testid="stPlotlyChart"],
[data-testid="stHorizontalBlock"] {
    background-color: var(--secondary-bg-color) !important;
    color: var(--text-color) !important;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 8px;
}

/* Fix white chart areas (Plotly, Vega-Lite, Matplotlib) */
.js-plotly-plot, .plot-container, canvas, svg {
    background-color: transparent !important;
    color: var(--text-color) !important;
}

/* Force Plotly charts to use dark theme */
.plotly .main-svg {
    background-color: transparent !important;
}

.plotly .bg {
    fill: transparent !important;
}

/* Fix Plotly hover tooltips */
.plotly .hovertext {
    background-color: #1a1d27 !important;
    color: #ffffff !important;
    border: 1px solid #4a4e5a !important;
    border-radius: 4px !important;
}

/* Executive clean text style (remove purple glow) */
h1, h2, h3 {
    color: #dbe3f0 !important;
    text-align: center;
    font-weight: 700;
    text-shadow: none !important;
}

/* Table */
table, th, td {
    background-color: #171b24 !important;
    color: #e1e1e1 !important;
}

/* Hover states */
div[data-testid="stMetric"]:hover {
    box-shadow: 0 0 12px rgba(74,168,224,0.25);
    transform: translateY(-1px);
    transition: 0.3s ease;
}

/* Scrollbars */
* {
    scrollbar-color: #333 #0e1016 !important;
}

/* Buttons, dropdowns, text fields */
button, select, input, textarea {
    background-color: #1a1d27 !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
}
button:hover {
    background-color: #26304a !important;
}

/* Links and icons */
a, svg, label {
    color: #70b8ff !important;
}

/* Remove duplicate mini title */
[data-testid="stHeadingContainer"] h1 + div {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("<h1>🎓 MIT Candidate Training Dashboard</h1>", unsafe_allow_html=True)
# ---- PAGE CONFIG ----

 


# ---- CUSTOM STYLING ----
st.markdown("""
    <style>
        :root {
            color-scheme: dark;
        }
        body, .stApp {
            background-color: #0b0e14 !important;
            color: #f5f5f5 !important;
        }
        h1, h2, h3, h4, h5, h6, p, span, div {
            color: #f5f5f5 !important;
        }
        div[data-testid="stMetricValue"] {
            font-size: 2rem !important;
            font-weight: 700 !important;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 1rem !important;
            color: #bbbbbb !important;
        }
        .stMetric {
            background: #15181e !important;
            border-radius: 16px !important;
            padding: 24px !important;
            box-shadow: 0 0 15px rgba(108, 99, 255, 0.15);
            text-align: center;
        }
        .data-source {
            background-color: #143d33;
            padding: 12px 18px;
            border-radius: 10px;
            font-weight: 500;
            color: #e1e1e1;
            box-shadow: 0 0 10px rgba(0,0,0,0.3);
        }
        [data-testid="stDataFrame"] {
            border-radius: 12px !important;
            overflow: hidden !important;
            box-shadow: 0 0 10px rgba(108, 99, 255, 0.15);
        }
        table {
            background-color: #14171c !important;
            border-collapse: collapse !important;
            width: 100%;
        }
        th {
            background-color: #1f2430 !important;
            color: #e1e1e1 !important;
            font-weight: 600 !important;
            text-transform: uppercase;
        }
        td {
            background-color: #171a21 !important;
            color: #d7d7d7 !important;
            font-size: 0.95rem !important;
            border-top: 1px solid #252a34 !important;
        }
        tr:hover td {
            background-color: #1e2230 !important;
        }
        .pending-title {
            font-size: 1.8rem !important;
            font-weight: 700 !important;
            color: #ffd95e !important;
            margin-bottom: 8px !important;
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
        .main-card {
            border: 1px solid rgba(108, 99, 255, 0.15);
            border-radius: 16px;
        }
    </style>
""", unsafe_allow_html=True)

# ---- LOAD DATA ----
@st.cache_data(ttl=300)
def load_data():
    main_data_url = (
        "https://docs.google.com/spreadsheets/d/e/"
        "2PACX-1vSbD6wUrZEt9kuSQpUT2pw0FMOb7h1y8xeX-hDTeiiZUPjtV0ohK_WcFtCSt_4nuxdtn9zqFS8z8aGw/"
        "pub?gid=1155015355&single=true&output=csv"
    )
    try:
        df = pd.read_csv(main_data_url, skiprows=4)
        data_source = "Google Sheets"
    except Exception as e:
        st.error(f"⚠️ Google Sheets error: {e}")
        return pd.DataFrame(), "Error"

    df = df.dropna(how="all")
    df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
    df = df.rename(columns={"Week ": "Week", "Start date": "Start Date"})
    if "Start Date" in df.columns:
        df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce")

    today = pd.Timestamp.now()

    def calc_weeks(row):
        start = row["Start Date"]
        if pd.isna(start):
            return None
        if start > today:
            return f"-{int((start - today).days / 7)} weeks from start"
        return int(((today - start).days // 7) + 1)

    df["Week"] = df.apply(calc_weeks, axis=1)
    df["Week"] = pd.to_numeric(df["Week"], errors="coerce")


    if "Salary" in df.columns:
        df["Salary"] = (
            df["Salary"]
            .astype(str)
            .str.replace("$", "")
            .str.replace(",", "")
            .str.replace(" ", "")
        )
        df["Salary"] = pd.to_numeric(df["Salary"], errors="coerce")

    df["Status"] = df["Status"].astype(str).str.strip().str.lower()
    return df, data_source


@st.cache_data(ttl=300)
def load_jobs_data():
    # ✅ Your real Open Jobs Google Sheets URL
    jobs_url = (
        "https://docs.google.com/spreadsheets/d/e/"
        "2PACX-1vSbD6wUrZEt9kuSQpUT2pw0FMOb7h1y8xeX-hDTeiiZUPjtV0ohK_WcFtCSt_4nuxdtn9zqFS8z8aGw/"
        "pub?gid=116813539&single=true&output=csv"
    )
    try:
        jobs_df = pd.read_csv(jobs_url, skiprows=5, header=0)
        jobs_df = jobs_df.loc[:, ~jobs_df.columns.str.contains("^Unnamed")]
        jobs_df = jobs_df.drop(columns=[c for c in ["JV Link", "JV ID"] if c in jobs_df.columns], errors="ignore")
        jobs_df = jobs_df.dropna(how="all").fillna("")
        return jobs_df
    except Exception as e:
        st.error(f"Error loading jobs data: {e}")
        return pd.DataFrame()

# ---- LOAD ----
st.cache_data.clear()
df, data_source = load_data()
jobs_df = load_jobs_data()

if df.empty:
    st.error("❌ Unable to load data.")
    st.stop()

# ---- HEADER ----
st.markdown('<div class="dashboard-title">🎓 MIT Candidate Training Dashboard</div>', unsafe_allow_html=True)
if data_source == "Google Sheets":
    st.success(f"📊 Data Source: {data_source} | Last Updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ---- METRICS ----
offer_pending = len(df[df["Status"] == "offer pending"])
offer_accepted = len(df[df["Status"] == "offer accepted"])
non_identified = len(df[df["Status"].isin(["free agent discussing opportunity", "unassigned", "training"])])
total_candidates = non_identified + offer_accepted

ready_for_placement = df[
    df["Week"].apply(lambda x: isinstance(x, (int, float)) and x > 6)
    & (~df["Status"].isin(["position identified", "offer pending", "offer accepted"]))
]
ready = len(ready_for_placement)

in_training = len(
    df[df["Status"].eq("training") & df["Week"].apply(lambda x: isinstance(x, (int, float)) and x <= 6)]
)
open_jobs = len(jobs_df) if not jobs_df.empty else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Candidates", total_candidates)
col2.metric("Open Positions", open_jobs)
col3.metric("Ready for Placement", ready)
col4.metric("In Training (Weeks 1–5)", in_training)
col5.metric("Offer Pending", offer_pending)

# ---- CHART ----
st.markdown("---")
left_col, right_col = st.columns([1, 1])
color_map = {
    "Ready for Placement": "#2E91E5",
    "In Training": "#E15F99",
    "Offer Pending": "#A020F0",
}
chart_data = pd.DataFrame({
    "Category": ["Ready for Placement", "In Training", "Offer Pending"],
    "Count": [ready, in_training, offer_pending]
})

with right_col:
    st.subheader("📊 Candidate Status Overview")
    fig_pie = px.pie(
        chart_data, names="Category", values="Count", hole=0.45,
        color="Category", color_discrete_map=color_map
    )
    fig_pie.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)", 
        font_color="white", 
        height=400,
        hoverlabel=dict(
            bgcolor="#1a1d27",
            font_color="white",
            font_size=12
        )
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with left_col:
    st.subheader("📍 Open Job Positions")
    if not jobs_df.empty:
        clean_jobs_df = jobs_df[jobs_df["Job Title"].notna()]
        st.dataframe(clean_jobs_df, use_container_width=True, height=400, hide_index=True)
    else:
        st.markdown('<div class="placeholder-box">No job positions data available</div>', unsafe_allow_html=True)

# ==========================================================
# READY FOR PLACEMENT SECTION
# ==========================================================
ready_df = df[
    df["Week"].apply(lambda x: isinstance(x, (int, float)) and x > 6)
    & (~df["Status"].isin(["position identified", "offer pending", "offer accepted"]))
    & (df["Status"].notna())
]

if not ready_df.empty:
    st.markdown("---")
    st.markdown("### 🧩 Ready for Placement Candidates")

    # Select relevant columns dynamically
    ready_cols = [col for col in ["MIT Name", "Training Site", "Location", "Week", "Salary", "Level"] if col in ready_df.columns]
    ready_display = ready_df[ready_cols].copy().fillna("—")

    # Clean salary formatting
    if "Salary" in ready_display.columns:
        ready_display["Salary"] = (
            ready_display["Salary"].astype(str).str.replace("$", "").str.replace(",", "").replace("nan", "TBD")
        )

    # Show table
    st.dataframe(
        ready_display,
        use_container_width=True,
        hide_index=True,
        height=(len(ready_display) * 35 + 60),
    )
    st.caption(f"{len(ready_display)} candidates are ready for placement — week > 6 and not yet placed.")
else:
    st.markdown('<div class="placeholder-box">No candidates currently ready for placement</div>', unsafe_allow_html=True)


# ==========================================================
# IN TRAINING SECTION
# ==========================================================
in_training_df = df[
    df["Status"].eq("training")
    & df["Week"].apply(lambda x: isinstance(x, (int, float)) and x <= 6)
]

if not in_training_df.empty:
    st.markdown("---")
    st.markdown("### 🏋️ In Training (Weeks 1–5)")

    train_cols = [col for col in ["MIT Name", "Training Site", "Location", "Week", "Salary", "Level"] if col in in_training_df.columns]
    train_display = in_training_df[train_cols].copy().fillna("—")

    if "Salary" in train_display.columns:
        train_display["Salary"] = (
            train_display["Salary"].astype(str).str.replace("$", "").str.replace(",", "").replace("nan", "TBD")
        )

    st.dataframe(
        train_display,
        use_container_width=True,
        hide_index=True,
        height=(len(train_display) * 35 + 60),
    )
    st.caption(f"{len(train_display)} candidates currently in training (weeks 1–5).")
else:
    st.markdown('<div class="placeholder-box">No candidates currently in training</div>', unsafe_allow_html=True)

# ==========================================================
# 🎯 CANDIDATE–JOB MATCH SCORE SECTION (Streamlined Executive View)
# ==========================================================
st.markdown("---")
st.markdown("### 🎯 Placement Readiness Breakdown")

# Filter relevant candidates
candidates_df = df[
    df["Status"].isin(["training", "unassigned", "free agent discussing opportunity"])
].copy()
candidates_df = candidates_df.dropna(subset=["MIT Name"])

if not jobs_df.empty and not candidates_df.empty:

    # ---- Salary parsing logic ----

    def parse_salary(s):
        if pd.isna(s):
            return None
        if isinstance(s, (int, float)):
            return float(s)
    
        # Clean string
        s = str(s).replace("$", "").replace(",", "").strip()
    
        # Normalize formats like "70,000 - 75,000" or "70k-75k"
        s = s.lower().replace("k", "000").replace("–", "-").replace("—", "-").replace("_", "-")
    
        if "-" in s:
            try:
                low, high = s.split("-")
                return (float(low.strip()), float(high.strip()))
            except ValueError:
                return None
        else:
            try:
                return float(s)
            except ValueError:
                return None

    def midpoint(val):
        if isinstance(val, tuple):
            return (val[0] + val[1]) / 2
        return val if isinstance(val, (int, float)) else None


# ---- Apply salary parsing and midpoint logic ----
    jobs_df["SalaryRange"] = jobs_df["Salary"].apply(parse_salary)
    candidates_df["SalaryRange"] = candidates_df["Salary"].apply(parse_salary)
    
    jobs_df["SalaryMid"] = jobs_df["SalaryRange"].apply(midpoint)
    candidates_df["SalaryMid"] = candidates_df["SalaryRange"].apply(midpoint)


    # ---- Calculate match scores (your scoring stays the same) ----
    match_results = []
    for _, c in candidates_df.iterrows():
        for _, j in jobs_df.iterrows():
            subscores = {}

            # 1) Vertical Alignment
            vert_score = 0
            c_vert = str(c.get("VERT", "")).strip().upper()
            j_vert = str(j.get("VERT", j.get("Vertical", ""))).strip().upper()
            if c_vert == j_vert:
                vert_score += 30
            exp_str = " ".join(
                str(c.get(k, "")).lower()
                for k in c.index if any(x in k.lower() for x in ["experience", "notes", "background"])
            )
            if "amazon" in exp_str or "aviation" in exp_str:
                vert_score += 10
            subscores["Vertical"] = vert_score

            # 2) Salary Trajectory
            c_sal, j_sal = c.get("SalaryMid"), j.get("SalaryMid")
            if j_sal and c_sal:
                if j_sal >= 1.05 * c_sal:
                    sal_score = 25
                elif abs(j_sal - c_sal) / c_sal <= 0.05:
                    sal_score = 15
                elif j_sal < 0.95 * c_sal:
                    sal_score = -10
                else:
                    sal_score = 0
            else:
                sal_score = 0
            subscores["Salary"] = sal_score

            # 3) Geographic Fit
            geo_score = 5
            cand_loc = str(c.get("Location", "")).strip().lower()
            job_city = str(j.get("City", "")).strip().lower()
            job_state = str(j.get("State", "")).strip().upper()
            if cand_loc == job_city:
                geo_score = 20
            elif cand_loc.endswith(job_state.lower()):
                geo_score = 10
            subscores["Geo"] = geo_score

            # 4) Confidence
            conf = str(c.get("Confidence", "")).lower()
            if "high" in conf:
                conf_score = 15
            elif "mod" in conf:
                conf_score = 10
            elif "low" in conf:
                conf_score = 5
            else:
                conf_score = 10
            subscores["Confidence"] = conf_score

            # 5) Readiness
            week = c.get("Week")
            if isinstance(week, (int, float)):
                if week >= 6:
                    ready_score = 10
                elif 1 <= week <= 5:
                    ready_score = week * 1.5
                else:
                    ready_score = 5
            else:
                ready_score = 5
            subscores["Readiness"] = ready_score

            total = sum(subscores.values())

            # Safe access for fields that may vary by sheet
            title_val = j.get("Title") or j.get("Job Title") or "—"
            vert_val = j.get("VERT") or j.get("Vertical") or "—"
            acct_val = j.get("Account") or j.get("Job Account") or "—"

            match_results.append({
                "Candidate": c["MIT Name"],
                "Job Account": acct_val,
                "Title": title_val,
                "City": j.get("City", ""),
                "State": j.get("State", ""),
                "VERT": vert_val,
                "Total Score": round(total, 1),
                "Week": c.get("Week"),
                "Status": c.get("Status")
            })

    match_df = pd.DataFrame(match_results)
    match_df = match_df.sort_values("Total Score", ascending=False)

    # Ready first, then training
    match_df["is_ready"] = (match_df["Week"] >= 6).astype(int)
    match_df = match_df.sort_values(["is_ready", "Week", "Total Score"], ascending=[False, False, False])

    # Expanders per candidate (ready auto-expanded)
    for candidate, group in match_df.groupby("Candidate", sort=False):
        week = group["Week"].iloc[0]
        status = "Ready for Placement" if week >= 6 else "In Training"
        color = "🟢" if week >= 6 else "🟡"
        expanded = True if week >= 6 else False

        top_jobs = group.nlargest(3, "Total Score")
        with st.expander(f"{color} {candidate} — {status} (Week {int(week)})", expanded=expanded):
            # iterate with dicts -> no KeyError from spaces/underscores
            for idx, rec in enumerate(top_jobs.to_dict(orient="records"), start=1):
                title = rec.get("Title", "—")
                account = rec.get("Job Account") or rec.get("Job_Account") or rec.get("Account") or "—"
                city = rec.get("City", "")
                state = rec.get("State", "")
                vert = rec.get("VERT", "—")
                score = rec.get("Total Score", 0)

                st.markdown(
                    f"**{idx}. {title} — {account}**  \n"
                    f"📍 {city}, {state} | 🏢 {vert} | ⭐ Match Score: {score}/100"
                )
            st.markdown("---")

else:
    st.markdown(
        '<div class="placeholder-box">No data available to compute match scores</div>',
        unsafe_allow_html=True
    )




# ---- OFFER PENDING SECTION ----
offer_pending_df = df[df["Status"].str.lower() == "offer pending"]
if not offer_pending_df.empty:
    st.markdown("---")
    st.markdown("### 🤝 Offer Pending Candidates")
    display_cols = [c for c in ["MIT Name", "Training Site", "Location", "Level"] if c in offer_pending_df.columns]
    offer_pending_display = offer_pending_df[display_cols].fillna("—")
    st.dataframe(offer_pending_display, use_container_width=True, hide_index=True)
    st.caption(f"{len(offer_pending_display)} candidates with pending offers – awaiting final approval/acceptance")
