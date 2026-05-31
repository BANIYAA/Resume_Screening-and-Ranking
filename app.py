"""
app.py
──────
Resume Screening — Enterprise Dashboard
Built with Streamlit · spaCy · Pandas

A premium, AI-free, local resume screening system.
"""

import streamlit as st
import pandas as pd
import time

from config_manager import (
    ensure_rules_file_exists,
    get_available_roles,
    load_role_rules,
    add_new_role,
    generate_keyword_config,
)
from parser_engine import process_resumes, clear_pipeline_cache


# ═══════════════════════════════════════════════
#  PAGE CONFIG & GLOBAL STYLES
# ═══════════════════════════════════════════════
st.set_page_config(
    page_title="ResumeIQ — Intelligent Screening",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Premium CSS injection ──────────────────────
st.markdown("""
<style>
/* ─── Google Font ─── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ─── Root Variables ─── */
:root {
    --bg-primary: #0a0e1a;
    --bg-secondary: #111827;
    --bg-card: #1a1f35;
    --bg-card-hover: #222845;
    --accent-primary: #6366f1;
    --accent-secondary: #8b5cf6;
    --accent-tertiary: #06b6d4;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
    --border: rgba(99, 102, 241, 0.15);
    --glow: rgba(99, 102, 241, 0.25);
}

/* ─── Global Reset ─── */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1629 0%, #131b33 100%) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}

/* ─── Hero Banner ─── */
.hero-banner {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 30%, #4338ca 60%, #6366f1 100%);
    border-radius: 16px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(99, 102, 241, 0.3);
    box-shadow: 0 20px 60px rgba(99, 102, 241, 0.15);
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(139,92,246,0.15) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-banner h1 {
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    margin: 0;
    color: #fff !important;
    position: relative;
}
.hero-banner p {
    font-size: 1.05rem;
    color: #c7d2fe !important;
    margin-top: 0.5rem;
    font-weight: 400;
    position: relative;
}

/* ─── Stat Cards ─── */
.stat-card {
    background: linear-gradient(145deg, var(--bg-card) 0%, rgba(99,102,241,0.06) 100%);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.5rem 1.8rem;
    text-align: center;
    transition: all 0.3s ease;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}
.stat-card:hover {
    transform: translateY(-4px);
    border-color: var(--accent-primary);
    box-shadow: 0 8px 30px var(--glow);
}
.stat-number {
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--accent-primary), var(--accent-tertiary));
    -webkit-background-clip: text;
    background-clip: text;
    line-height: 1.1;
}
.stat-label {
    font-size: 0.82rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
    margin-top: 0.5rem;
}

/* ─── Status Badges ─── */
.badge-excellent {
    background: linear-gradient(135deg, #065f46, #059669);
    color: #d1fae5;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    display: inline-block;
}
.badge-good {
    background: linear-gradient(135deg, #1e3a5f, #2563eb);
    color: #dbeafe;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    display: inline-block;
}
.badge-average {
    background: linear-gradient(135deg, #78350f, #d97706);
    color: #fef3c7;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    display: inline-block;
}
.badge-low {
    background: linear-gradient(135deg, #7f1d1d, #dc2626);
    color: #fee2e2;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    display: inline-block;
}

/* ─── Candidate Card ─── */
.candidate-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.4rem 1.8rem;
    margin-bottom: 1rem;
    transition: all 0.25s ease;
}
.candidate-card:hover {
    border-color: var(--accent-primary);
    box-shadow: 0 4px 24px var(--glow);
}
.candidate-card h4 {
    margin: 0 0 0.4rem 0;
    color: var(--text-primary);
    font-weight: 700;
}
.candidate-card .meta {
    color: var(--text-secondary);
    font-size: 0.88rem;
}

/* ─── Section Headers ─── */
.section-header {
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 1.5rem 0 1rem 0;
    padding-bottom: 0.6rem;
    border-bottom: 2px solid var(--border);
    display: flex;
    align-items: center;
    gap: 0.6rem;
}

/* ─── Skill Tags ─── */
.skill-tag {
    display: inline-block;
    background: rgba(99, 102, 241, 0.12);
    color: #a5b4fc;
    border: 1px solid rgba(99, 102, 241, 0.25);
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 500;
    margin: 2px 4px 2px 0;
}

/* ─── Tab Styling ─── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: var(--bg-secondary) !important;
    border-radius: 12px;
    padding: 4px;
    border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 10px 24px;
    font-weight: 600;
    color: var(--text-secondary) !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    background: var(--accent-primary) !important;
    color: #fff !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 1.5rem;
}

/* ─── Buttons ─── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary)) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 2rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(99, 102, 241, 0.45) !important;
}

.stDownloadButton > button {
    background: linear-gradient(135deg, #059669, #10b981) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 2rem !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3) !important;
}

/* ─── Inputs & Selects ─── */
.stSelectbox > div > div,
.stTextInput > div > div > input,
.stFileUploader > div {
    background: var(--bg-card) !important;
    border-color: var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: 10px !important;
}

/* ─── DataFrame ─── */
.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid var(--border);
}

/* ─── Progress Bar ─── */
.progress-bar-container {
    background: rgba(99, 102, 241, 0.1);
    border-radius: 10px;
    overflow: hidden;
    height: 10px;
    margin-top: 6px;
}
.progress-bar-fill {
    height: 100%;
    border-radius: 10px;
    transition: width 0.6s ease;
}

/* ─── Form ─── */
[data-testid="stForm"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 1.8rem !important;
}

/* ─── Divider ─── */
hr {
    border-color: var(--border) !important;
}

/* ─── Metrics ─── */
[data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
}
[data-testid="stMetricLabel"] {
    color: var(--text-secondary) !important;
}

/* ─── Success/Error/Warning boxes ─── */
.stAlert {
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═══════════════════════════════════════════════
def get_favorability_badge(pct: float) -> str:
    if pct >= 75:
        return '<span class="badge-excellent">★ Excellent</span>'
    elif pct >= 55:
        return '<span class="badge-good">● Good</span>'
    elif pct >= 35:
        return '<span class="badge-average">◐ Average</span>'
    else:
        return '<span class="badge-low">○ Low Match</span>'


def get_progress_color(pct: float) -> str:
    if pct >= 75:
        return "linear-gradient(90deg, #059669, #10b981)"
    elif pct >= 55:
        return "linear-gradient(90deg, #2563eb, #3b82f6)"
    elif pct >= 35:
        return "linear-gradient(90deg, #d97706, #f59e0b)"
    else:
        return "linear-gradient(90deg, #dc2626, #ef4444)"


# ═══════════════════════════════════════════════
#  INIT STATE
# ═══════════════════════════════════════════════
ensure_rules_file_exists()

if "results_df" not in st.session_state:
    st.session_state.results_df = None
if "processing_done" not in st.session_state:
    st.session_state.processing_done = False


# ═══════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1.5rem 0 1rem 0;">
        <div style="font-size: 2.5rem; margin-bottom: 0.3rem;">📋</div>
        <div style="font-size: 1.3rem; font-weight: 800;
                    background: linear-gradient(135deg, #6366f1, #06b6d4);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;">ResumeIQ</div>
        <div style="font-size: 0.75rem; color: #64748b; letter-spacing: 0.1em;
                    text-transform: uppercase; font-weight: 600; margin-top: 2px;">
            Intelligent Screening Engine</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Role selector
    roles = get_available_roles()
    selected_role = st.selectbox(
        "🎯  Target Job Role",
        options=roles,
        index=0,
        help="Select the role to screen resumes against.",
    )

    # Show role stats
    if selected_role:
        config = generate_keyword_config(selected_role)
        kw_count = len(set(config["keyword_weights"].values()))
        st.markdown(f"""
        <div style="background: rgba(99,102,241,0.08); border: 1px solid rgba(99,102,241,0.2);
                    border-radius: 10px; padding: 1rem; margin-top: 0.8rem;">
            <div style="font-size: 0.78rem; color: #94a3b8; text-transform: uppercase;
                        letter-spacing: 0.08em; font-weight: 600;">Role Configuration</div>
            <div style="margin-top: 0.7rem; font-size: 0.88rem;">
                <div>🔑 <strong>{len(config['keyword_weights'])}</strong> keyword variations</div>
                <div style="margin-top: 0.3rem;">📊 <strong>{config['max_possible_score']}</strong> max score points</div>
                <div style="margin-top: 0.3rem;">🧩 <strong>{len(config['entity_patterns'])}</strong> NLP patterns</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-size: 0.75rem; color: #475569; text-align: center; padding: 0.5rem 0;">
        <div style="font-weight: 600; color: #64748b;">100% Local Processing</div>
        <div style="margin-top: 3px;">No APIs · No Token Costs</div>
        <div style="margin-top: 3px;">spaCy NLP · pdfplumber</div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════
#  MAIN CONTENT — TABS
# ═══════════════════════════════════════════════

# Hero banner
st.markdown("""
<div class="hero-banner">
    <h1>📋 ResumeIQ — Intelligent Screening</h1>
    <p>AI-free local NLP engine for bulk candidate ranking, favorability scoring, and dynamic rule management.</p>
</div>
""", unsafe_allow_html=True)

tab_screen, tab_manage, tab_insights = st.tabs([
    "🏆  Candidate Ranking",
    "⚙️  Role & Rule Management",
    "📊  Rule Inspector",
])


# ═══════════════════════════════════════════════
#  TAB 1 — CANDIDATE RANKING
# ═══════════════════════════════════════════════
with tab_screen:

    # Upload section
    st.markdown('<div class="section-header">📄 Upload Resumes</div>', unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Drag & drop resume PDFs here",
        type=["pdf"],
        accept_multiple_files=True,
        key="resume_uploader",
        help="Upload one or more PDF resumes for bulk screening.",
    )

    col_info, col_btn = st.columns([3, 1])
    with col_info:
        if uploaded_files:
            st.markdown(
                f'<div style="color: var(--accent-tertiary); font-weight: 600;">'
                f'📂 {len(uploaded_files)} file(s) selected — Role: <code>{selected_role}</code></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="color: #64748b;">No files uploaded yet. Upload PDFs above to begin screening.</div>',
                unsafe_allow_html=True,
            )

    with col_btn:
        process_clicked = st.button(
            "🚀 Process Resumes",
            disabled=not uploaded_files,
            use_container_width=True,
        )

    # ── Processing ──
    if process_clicked and uploaded_files:
        clear_pipeline_cache()

        progress_bar = st.progress(0, text="Initializing NLP pipeline...")
        status_text = st.empty()

        results = []
        total = len(uploaded_files)

        for i, f in enumerate(uploaded_files):
            status_text.markdown(
                f'<div style="color: #94a3b8;">Processing <strong>{f.name}</strong> '
                f'({i+1}/{total})...</div>',
                unsafe_allow_html=True,
            )
            progress_bar.progress((i + 1) / total, text=f"Processing {i+1}/{total}...")

            single_result = process_resumes([f], selected_role)
            results.extend(single_result)

        progress_bar.empty()
        status_text.empty()

        # Build DataFrame
        df = pd.DataFrame(results)
        df = df.rename(columns={
            "file_name": "Candidate",
            "total_score": "Score",
            "favorability_pct": "Favorability %",
            "skills_found": "Skills Found",
            "years_of_experience": "Experience (yrs)",
            "max_possible_score": "Max Score",
            "status": "Status",
        })
        df = df.sort_values("Favorability %", ascending=False).reset_index(drop=True)
        df.index = df.index + 1  # 1-based ranking
        df.index.name = "Rank"

        st.session_state.results_df = df
        st.session_state.processing_done = True

    # ── Display results ──
    if st.session_state.processing_done and st.session_state.results_df is not None:
        df = st.session_state.results_df

        st.markdown("---")

        # Summary stats
        st.markdown('<div class="section-header">📈 Screening Summary</div>', unsafe_allow_html=True)

        total_candidates = len(df)
        excellent = len(df[df["Favorability %"] >= 75])
        good = len(df[(df["Favorability %"] >= 55) & (df["Favorability %"] < 75)])
        avg_fav = df["Favorability %"].mean()

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{total_candidates}</div>
                <div class="stat-label">Total Candidates</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{excellent}</div>
                <div class="stat-label">Excellent Match (≥75%)</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{good}</div>
                <div class="stat-label">Good Match (≥55%)</div>
            </div>""", unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{avg_fav:.1f}%</div>
                <div class="stat-label">Average Favorability</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Candidate cards ──
        st.markdown('<div class="section-header">🏆 Ranked Candidates</div>', unsafe_allow_html=True)

        for idx, row in df.iterrows():
            fav = row["Favorability %"]
            badge = get_favorability_badge(fav)
            bar_color = get_progress_color(fav)
            skills_list = row["Skills Found"]
            if isinstance(skills_list, list):
                skills_html = " ".join([f'<span class="skill-tag">{s}</span>' for s in skills_list])
            else:
                skills_html = '<span class="skill-tag">—</span>'

            exp_text = f'{row["Experience (yrs)"]} yrs' if row["Experience (yrs)"] else "Not specified"

            st.markdown(f"""
            <div class="candidate-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4>#{idx} &nbsp; {row['Candidate']}</h4>
                        <div class="meta">
                            Score: <strong>{row['Score']}</strong> / {row['Max Score']}
                            &nbsp;·&nbsp; Experience: <strong>{exp_text}</strong>
                            &nbsp;·&nbsp; {row['Status']}
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.8rem; font-weight: 800;
                                    background: {bar_color};
                                    -webkit-background-clip: text;
                                    -webkit-text-fill-color: transparent;">{fav}%</div>
                        {badge}
                    </div>
                </div>
                <div class="progress-bar-container" style="margin-top: 10px;">
                    <div class="progress-bar-fill" style="width: {fav}%; background: {bar_color};"></div>
                </div>
                <div style="margin-top: 10px;">{skills_html}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Data table ──
        st.markdown('<div class="section-header">📋 Full Data Table</div>', unsafe_allow_html=True)

        display_df = df.copy()
        display_df["Skills Found"] = display_df["Skills Found"].apply(
            lambda x: ", ".join(x) if isinstance(x, list) else str(x)
        )
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400,
        )

        # ── Export ──
        st.markdown("<br>", unsafe_allow_html=True)
        export_df = display_df.copy()
        csv_data = export_df.to_csv(index=True)

        col_dl, _ = st.columns([1, 3])
        with col_dl:
            st.download_button(
                label="📥 Export Rankings as CSV",
                data=csv_data,
                file_name=f"resume_rankings_{selected_role}.csv",
                mime="text/csv",
                use_container_width=True,
            )


# ═══════════════════════════════════════════════
#  TAB 2 — ROLE & RULE MANAGEMENT
# ═══════════════════════════════════════════════
with tab_manage:

    col_left, col_right = st.columns([1, 1], gap="large")

    # ── Add new role ──
    with col_left:
        st.markdown('<div class="section-header">➕ Create New Job Role</div>', unsafe_allow_html=True)

        st.markdown("""
        <div style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 1rem;">
            Add a new role to the screening system. This creates a new sheet in
            <code>Screening_Rules.xlsx</code> with template headers, ready for you
            to populate with keywords and weights.
        </div>
        """, unsafe_allow_html=True)

        with st.form("add_role_form", clear_on_submit=True):
            new_role_name = st.text_input(
                "Role Name",
                placeholder="e.g. Frontend_Developer",
                help="Use underscores for spaces. Max 31 characters (Excel sheet name limit).",
            )
            submitted = st.form_submit_button("🆕 Create Role", use_container_width=True)

            if submitted:
                if new_role_name.strip():
                    success, msg = add_new_role(new_role_name)
                    if success:
                        clear_pipeline_cache()
                        st.success(f"✅ {msg}")
                        st.toast(f"Role '{new_role_name}' created!", icon="🎉")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")
                else:
                    st.warning("⚠️ Please enter a role name.")

    # ── Current roles overview ──
    with col_right:
        st.markdown('<div class="section-header">📂 Existing Roles</div>', unsafe_allow_html=True)

        current_roles = get_available_roles()
        for role in current_roles:
            cfg = generate_keyword_config(role)
            kw_count = len(cfg["keyword_weights"])
            max_sc = cfg["max_possible_score"]

            st.markdown(f"""
            <div class="candidate-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4>🏷️ {role}</h4>
                        <div class="meta">
                            {kw_count} keyword variations · Max score: {max_sc}
                        </div>
                    </div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: var(--accent-primary);">
                        {len(cfg['entity_patterns'])} <span style="font-size: 0.7rem;
                        color: var(--text-muted); font-weight: 500;">patterns</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div style="background: rgba(6,182,212,0.08); border: 1px solid rgba(6,182,212,0.2);
                border-radius: 12px; padding: 1.2rem 1.5rem; margin-top: 0.5rem;">
        <div style="font-weight: 700; color: #06b6d4; font-size: 0.95rem;">
            💡 How to Edit Rules
        </div>
        <div style="color: #94a3b8; font-size: 0.88rem; margin-top: 0.5rem; line-height: 1.6;">
            Open <code>Screening_Rules.xlsx</code> in Excel or Google Sheets. Each sheet tab is a role.
            Add rows with columns: <strong>Keyword</strong>, <strong>Category</strong>,
            <strong>Weight</strong> (numeric), and <strong>Synonyms</strong> (comma-separated).
            Changes take effect on the next processing run.
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════
#  TAB 3 — RULE INSPECTOR
# ═══════════════════════════════════════════════
with tab_insights:

    st.markdown('<div class="section-header">🔍 Rule Inspector</div>', unsafe_allow_html=True)

    inspect_role = st.selectbox(
        "Select role to inspect",
        options=get_available_roles(),
        key="inspect_role_select",
    )

    if inspect_role:
        rules_df = load_role_rules(inspect_role)
        config_data = generate_keyword_config(inspect_role)

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown(f"""
            <div class="stat-card" style="text-align: left;">
                <div style="font-weight: 700; font-size: 1rem; margin-bottom: 0.8rem;">
                    📝 Rules Table — {inspect_role}
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(
                rules_df[["Keyword", "Category", "Weight", "Synonyms"]],
                use_container_width=True,
                height=400,
            )

        with col_b:
            st.markdown("""
            <div class="stat-card" style="text-align: left;">
                <div style="font-weight: 700; font-size: 1rem; margin-bottom: 0.8rem;">
                    📊 Weight Distribution
                </div>
            </div>
            """, unsafe_allow_html=True)

            if not rules_df.empty:
                chart_data = rules_df[["Keyword", "Weight"]].sort_values("Weight", ascending=True)
                st.bar_chart(chart_data.set_index("Keyword"), horizontal=True, height=400)

        # Keyword expansion view
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">🧩 Expanded Keyword Map</div>', unsafe_allow_html=True)

        kw_data = []
        for variation, weight in sorted(config_data["keyword_weights"].items(), key=lambda x: -x[1]):
            kw_data.append({"Variation": variation, "Weight": weight})

        if kw_data:
            kw_df = pd.DataFrame(kw_data)
            st.dataframe(kw_df, use_container_width=True, height=300)
