"""
Intelli-Credit: AI-Powered Corporate Credit Decision Engine
v2.0 — Complete UI overhaul with professional banking theme
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import re
import io
from risk_engine import (
    calculate_ratios, calculate_risk, analyze_primary_notes,
    get_ews_signals, recommend_loan, INDUSTRY_RISK_MAP
)
from cam_generator import generate_cam
from database import save_application, get_all_applications, get_portfolio_stats, delete_application
from ml_engine import ml_predict, get_feature_importance, FEATURE_LABELS

# ── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Intelli-Credit | Corporate Credit Engine",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

/* ── Background ── */
.stApp {
    background: #030d1a;
    background-image:
        radial-gradient(ellipse at 20% 0%, rgba(13,33,55,0.9) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 100%, rgba(11,28,54,0.7) 0%, transparent 60%);
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #041120 0%, #071929 100%);
    border-right: 1px solid rgba(201,151,74,0.25);
}
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #c9974a !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}

/* ── Main header ── */
.main-header {
    background: linear-gradient(135deg, #0d2137 0%, #0a1929 60%, #112240 100%);
    border: 1px solid rgba(201,151,74,0.35);
    border-radius: 12px;
    padding: 28px 36px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.main-header::before {
    content: '';
    position: absolute;
    top: -30px; right: -30px;
    width: 180px; height: 180px;
    background: radial-gradient(circle, rgba(201,151,74,0.12), transparent 70%);
    border-radius: 50%;
}
.main-header h1 {
    color: #ffffff;
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin: 0 0 4px 0;
}
.main-header p {
    color: rgba(255,255,255,0.55);
    font-size: 0.9rem;
    margin: 0;
}
.header-badge {
    display: inline-block;
    background: rgba(201,151,74,0.18);
    color: #c9974a;
    border: 1px solid rgba(201,151,74,0.4);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    margin-bottom: 10px;
}

/* ── Section cards ── */
.section-card {
    background: linear-gradient(135deg, #0d1f35 0%, #091929 100%);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 22px 24px;
    margin-bottom: 18px;
}
.section-title {
    color: #c9974a;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-bottom: 16px;
    border-bottom: 1px solid rgba(201,151,74,0.2);
    padding-bottom: 8px;
}

/* ── Metric cards ── */
.metric-card {
    background: rgba(13,33,55,0.7);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    padding: 14px 16px;
    text-align: center;
}
.metric-label {
    color: rgba(255,255,255,0.45);
    font-size: 0.7rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.metric-value {
    color: #ffffff;
    font-size: 1.6rem;
    font-weight: 700;
    font-family: 'IBM Plex Mono', monospace;
    line-height: 1;
}
.metric-sub {
    color: rgba(255,255,255,0.35);
    font-size: 0.7rem;
    margin-top: 4px;
}

/* ── Decision banners ── */
.decision-low {
    background: linear-gradient(135deg, rgba(16,85,50,0.4), rgba(5,46,22,0.6));
    border: 1.5px solid rgba(34,197,94,0.5);
    border-radius: 10px;
    padding: 20px 24px;
    text-align: center;
}
.decision-medium {
    background: linear-gradient(135deg, rgba(120,53,15,0.4), rgba(92,45,10,0.6));
    border: 1.5px solid rgba(245,158,11,0.5);
    border-radius: 10px;
    padding: 20px 24px;
    text-align: center;
}
.decision-high {
    background: linear-gradient(135deg, rgba(127,29,29,0.4), rgba(69,10,10,0.6));
    border: 1.5px solid rgba(239,68,68,0.5);
    border-radius: 10px;
    padding: 20px 24px;
    text-align: center;
}
.decision-title {
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    margin-bottom: 4px;
}
.decision-sub {
    font-size: 0.85rem;
    opacity: 0.7;
}

/* ── Risk reason pills ── */
.risk-pill-red {
    display: inline-block;
    background: rgba(127,29,29,0.3);
    border: 1px solid rgba(239,68,68,0.4);
    color: #fca5a5;
    border-radius: 20px;
    padding: 5px 12px;
    font-size: 0.8rem;
    margin: 3px 2px;
}
.risk-pill-yellow {
    display: inline-block;
    background: rgba(120,53,15,0.3);
    border: 1px solid rgba(245,158,11,0.4);
    color: #fde68a;
    border-radius: 20px;
    padding: 5px 12px;
    font-size: 0.8rem;
    margin: 3px 2px;
}
.risk-pill-green {
    display: inline-block;
    background: rgba(5,46,22,0.4);
    border: 1px solid rgba(34,197,94,0.4);
    color: #86efac;
    border-radius: 20px;
    padding: 5px 12px;
    font-size: 0.8rem;
    margin: 3px 2px;
}

/* ── EWS signals ── */
.ews-critical {
    background: rgba(127,29,29,0.25);
    border-left: 3px solid #ef4444;
    border-radius: 0 6px 6px 0;
    padding: 8px 14px;
    margin: 5px 0;
    color: #fca5a5;
    font-size: 0.82rem;
}
.ews-watch {
    background: rgba(120,53,15,0.25);
    border-left: 3px solid #f59e0b;
    border-radius: 0 6px 6px 0;
    padding: 8px 14px;
    margin: 5px 0;
    color: #fde68a;
    font-size: 0.82rem;
}
.ews-clear {
    background: rgba(5,46,22,0.25);
    border-left: 3px solid #22c55e;
    border-radius: 0 6px 6px 0;
    padding: 8px 14px;
    margin: 5px 0;
    color: #86efac;
    font-size: 0.82rem;
}

/* ── Streamlit overrides ── */
.stButton > button {
    background: linear-gradient(135deg, #c9974a, #b07d35);
    color: #000000;
    font-weight: 700;
    font-family: 'IBM Plex Sans', sans-serif;
    border: none;
    border-radius: 8px;
    padding: 0.55rem 1.5rem;
    font-size: 0.9rem;
    letter-spacing: 0.02em;
    width: 100%;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.88; }

div[data-testid="stMetricValue"] { color: #ffffff !important; }
div[data-testid="stMetricLabel"] { color: rgba(255,255,255,0.5) !important; font-size: 0.72rem !important; }

.stNumberInput label, .stTextInput label,
.stSelectbox label, .stTextArea label, .stSlider label {
    color: rgba(255,255,255,0.65) !important;
    font-size: 0.78rem !important;
    font-weight: 500;
}

input, textarea, select {
    background: rgba(255,255,255,0.05) !important;
    color: #ffffff !important;
    border-color: rgba(255,255,255,0.15) !important;
}
.stDivider { border-color: rgba(255,255,255,0.07) !important; }

/* ── Download button ── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #1a4a6e, #0f3050) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab"] {
    color: rgba(255,255,255,0.5);
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.82rem;
    font-weight: 500;
    letter-spacing: 0.05em;
}
.stTabs [aria-selected="true"] {
    color: #c9974a !important;
    border-bottom-color: #c9974a !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #030d1a; }
::-webkit-scrollbar-thumb { background: rgba(201,151,74,0.4); border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ──────────────────────────────────────────────────────────
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — ALL INPUTS
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🏢 Company Profile")
    company_name  = st.text_input("Company Name", placeholder="e.g. Acme Industries Ltd.")
    industry      = st.selectbox("Industry Sector", list(INDUSTRY_RISK_MAP.keys()))
    loan_amount   = st.number_input("Loan Amount Requested (₹)", min_value=0.0, step=100000.0,
                                    format="%.0f")
    risk_mode     = st.selectbox("Assessment Mode", ["Balanced", "Conservative", "Aggressive"])

    st.markdown("---")
    st.markdown("### 📊 Financials — P&L")
    current_revenue  = st.number_input("Current Year Revenue (₹)",  min_value=0.0, step=100000.0, format="%.0f")
    previous_revenue = st.number_input("Previous Year Revenue (₹)", min_value=0.0, step=100000.0, format="%.0f")
    ebitda           = st.number_input("EBITDA (₹)",                min_value=0.0, step=100000.0, format="%.0f")
    operating_income = st.number_input("Operating Income / PAT (₹)",min_value=0.0, step=100000.0, format="%.0f")
    interest_expense = st.number_input("Interest Expense (₹)",      min_value=0.0, step=10000.0,  format="%.0f")

    st.markdown("### 🏦 Financials — Balance Sheet")
    total_debt        = st.number_input("Total Debt (₹)",            min_value=0.0, step=100000.0, format="%.0f")
    equity            = st.number_input("Total Equity (₹)",          min_value=0.0, step=100000.0, format="%.0f")
    current_assets    = st.number_input("Current Assets (₹)",        min_value=0.0, step=100000.0, format="%.0f")
    current_liabs     = st.number_input("Current Liabilities (₹)",   min_value=0.0, step=100000.0, format="%.0f")
    loan_obligation   = st.number_input("Annual Debt Repayment (₹)", min_value=0.0, step=10000.0,  format="%.0f")

    st.markdown("### ⚖️ Qualitative Factors")
    promoter_stake   = st.slider("Promoter Equity Stake (%)", 0, 100, 51)
    litigation_level = st.selectbox("Litigation Exposure", ["Low", "Medium", "High"])
    negative_news    = st.number_input("Negative News Count", min_value=0, step=1)
    primary_notes    = st.text_area("Credit Officer Notes", placeholder="Enter due-diligence observations...", height=110)

    st.markdown("### 🇮🇳 Indian Context")
    gst_compliance = st.selectbox("GST Filing Compliance", ["Regular & Compliant", "Minor Delays", "Frequent Defaults", "Not Registered"])
    cibil_score    = st.number_input("CIBIL Commercial Score (1–10)", min_value=0.0, max_value=10.0, step=0.1, value=7.0)
    mca_status     = st.selectbox("MCA21 / ROC Filing Status", ["Up to Date", "Minor Delays", "Significant Gaps", "Not Filed"])

    st.markdown("### 📁 Upload Annual Report PDF")
    uploaded_pdf = st.file_uploader("Upload PDF (Annual Report / Financials)", type=["pdf"])
    pdf_extracted_notes = ""
    if uploaded_pdf is not None:
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(uploaded_pdf.read()))
            raw_text = " ".join(page.extract_text() or "" for page in reader.pages[:15])
            rev_match    = re.findall(r'(?:revenue|turnover)[^\d]{0,20}([\d,]+(?:\.\d+)?)', raw_text, re.IGNORECASE)
            profit_match = re.findall(r'(?:ebitda|operating profit)[^\d]{0,20}([\d,]+(?:\.\d+)?)', raw_text, re.IGNORECASE)
            pdf_extracted_notes = raw_text[:2000]
            st.success(f"✅ PDF parsed — {len(reader.pages)} pages")
            if rev_match:   st.info(f"Revenue figures: {', '.join(rev_match[:3])}")
            if profit_match: st.info(f"EBITDA figures: {', '.join(profit_match[:3])}")
            with st.expander("View Extracted Text"):
                st.text(raw_text[:600])
        except Exception as e:
            st.warning(f"PDF note: {str(e)[:80]}")

    st.markdown("---")
    analyze_btn = st.button("🚀  Run Credit Analysis", use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN AREA
# ══════════════════════════════════════════════════════════════════════════════

# ── Header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <div class="header-badge">AI-POWERED  •  EXPLAINABLE  •  REAL-TIME</div>
  <h1>🏦 Intelli-Credit</h1>
  <p>Corporate Credit Decision Engine  —  Automated risk assessment aligned with bank-grade underwriting standards</p>
</div>
""", unsafe_allow_html=True)

# ── Analysis trigger ───────────────────────────────────────────────────────
if analyze_btn:
    with st.spinner("Running credit analysis..."):
        dscr, debt_equity, revenue_growth, icr, ebitda_margin, current_ratio = calculate_ratios(
            current_revenue, previous_revenue, operating_income,
            loan_obligation, total_debt, equity,
            ebitda, interest_expense,
            current_assets, current_liabs
        )

        (score, category, decision, confidence,
         reasons, positives,
         capacity_risk, capital_risk,
         character_risk, conditions_risk) = calculate_risk(
            dscr, debt_equity, revenue_growth,
            icr, ebitda_margin, current_ratio,
            litigation_level, negative_news,
            promoter_stake, industry, risk_mode
        )

        note_adj, note_insights = analyze_primary_notes(primary_notes + " " + pdf_extracted_notes)
        score   = max(0, min(100, score + note_adj))

        # ── Indian Context Adjustments ─────────────────────────────────
        indian_flags = []
        if gst_compliance == "Frequent Defaults":
            score += 15; indian_flags.append("🔴 Frequent GST filing defaults — revenue inflation risk.")
        elif gst_compliance == "Minor Delays":
            score += 5;  indian_flags.append("🟡 GST filing delays noted — verify GSTR-2A vs 3B reconciliation.")
        elif gst_compliance == "Not Registered":
            score += 20; indian_flags.append("⛔ GST not registered — regulatory non-compliance.")
        else:
            positives.append("✅ GST filings regular and compliant.")

        if cibil_score < 4:
            score += 20; indian_flags.append(f"🔴 Low CIBIL Commercial Score ({cibil_score}) — poor credit history.")
        elif cibil_score < 6:
            score += 10; indian_flags.append(f"🟡 CIBIL score {cibil_score} — below acceptable range.")
        elif cibil_score >= 8:
            positives.append(f"✅ Strong CIBIL Commercial Score ({cibil_score}).")

        if mca_status in ["Significant Gaps", "Not Filed"]:
            score += 15; indian_flags.append("🔴 MCA21/ROC filing non-compliance — governance concern.")
        elif mca_status == "Minor Delays":
            score += 5;  indian_flags.append("🟡 MCA21 minor delays — monitor compliance.")

        score   = max(0, min(100, score))
        reasons = note_insights + indian_flags + reasons

        # Re-classify after note adjustment
        if score <= 28:
            category = "Low Risk";    decision = "Recommend Approval"
        elif score <= 55:
            category = "Medium Risk"; decision = "Approve with Conditions"
        else:
            category = "High Risk";   decision = "Recommend Rejection"

        loan_rec = recommend_loan(score, category, loan_amount, dscr, debt_equity, ebitda)

        ews_signals = get_ews_signals(dscr, revenue_growth, debt_equity, icr, current_ratio, negative_news)

        # ── ML Prediction + SHAP ──────────────────────────────────────
        try:
            ml_result = ml_predict({
                "dscr": dscr, "debt_equity": debt_equity,
                "revenue_growth": revenue_growth, "icr": icr,
                "ebitda_margin": ebitda_margin, "current_ratio": current_ratio,
                "litigation_level": litigation_level, "negative_news": negative_news,
                "promoter_stake": promoter_stake, "industry": industry,
                "gst_compliance": gst_compliance, "cibil_score": cibil_score,
            })
        except Exception:
            ml_result = None

        st.session_state.analysis_done = True
        st.session_state.data = {
            "company_name": company_name, "industry": industry,
            "loan_amount": loan_amount,   "risk_mode": risk_mode,
            "dscr": dscr, "debt_equity": debt_equity, "revenue_growth": revenue_growth,
            "icr": icr, "ebitda_margin": ebitda_margin, "current_ratio": current_ratio,
            "score": score, "category": category, "decision": decision, "confidence": confidence,
            "reasons": reasons, "positives": positives,
            "capacity_risk": capacity_risk, "capital_risk": capital_risk,
            "character_risk": character_risk, "conditions_risk": conditions_risk,
            "ews_signals": ews_signals, "loan_rec": loan_rec, "ml_result": ml_result,
            "gst_compliance": gst_compliance, "cibil_score": cibil_score, "mca_status": mca_status,
            # for simulation
            "current_revenue": current_revenue, "previous_revenue": previous_revenue,
            "operating_income": operating_income, "loan_obligation": loan_obligation,
            "total_debt": total_debt, "equity": equity, "ebitda": ebitda,
            "interest_expense": interest_expense,
            "current_assets": current_assets, "current_liabs": current_liabs,
            "litigation_level": litigation_level, "negative_news": negative_news,
            "promoter_stake": promoter_stake,
        }

        # ── Auto-save to database ──────────────────────────────────────
        try:
            saved_id = save_application(st.session_state.data)
            st.session_state.last_saved_id = saved_id
        except Exception:
            pass

# ══════════════════════════════════════════════════════════════════════════════
# RESULTS
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.analysis_done:
    d = st.session_state.data

    # ── DECISION BANNER ─────────────────────────────────────────────────
    if d["category"] == "Low Risk":
        css_cls   = "decision-low"
        icon      = "🟢"
        score_col = "#22c55e"
    elif d["category"] == "Medium Risk":
        css_cls   = "decision-medium"
        icon      = "🟡"
        score_col = "#f59e0b"
    else:
        css_cls   = "decision-high"
        icon      = "🔴"
        score_col = "#ef4444"

    st.markdown(f"""
    <div class="{css_cls}">
        <div class="decision-title" style="color:{score_col}">
            {icon}  {d['category'].upper()}  —  {d['decision']}
        </div>
        <div class="decision-sub" style="color:rgba(255,255,255,0.6)">
            {d['company_name'] or 'Company'}  &nbsp;|&nbsp;
            Risk Score: <b style="color:{score_col}">{d['score']}/100</b>  &nbsp;|&nbsp;
            Confidence: <b>{d['confidence']}%</b>  &nbsp;|&nbsp;
            Mode: {d['risk_mode']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── LOAN RECOMMENDATION CARD ────────────────────────────────────────
    lr = d["loan_rec"]
    lr_color = "#22c55e" if d["category"] == "Low Risk" else ("#f59e0b" if d["category"] == "Medium Risk" else "#ef4444")
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0d2137,#091929);border:1px solid {lr_color}55;
                border-radius:10px;padding:18px 24px;margin-bottom:18px;">
        <div style="color:#c9974a;font-size:0.72rem;font-weight:600;letter-spacing:0.14em;
                    text-transform:uppercase;margin-bottom:12px;">
            🏦 Loan Recommendation Engine
        </div>
        <div style="display:flex;gap:24px;flex-wrap:wrap;align-items:center;">
            <div style="text-align:center;min-width:140px;">
                <div style="color:rgba(255,255,255,0.4);font-size:0.68rem;letter-spacing:0.1em;text-transform:uppercase">Sanctioned Amount</div>
                <div style="color:{lr_color};font-size:1.5rem;font-weight:700;font-family:'IBM Plex Mono',monospace">
                    {"₹ {:,.0f}".format(lr['sanctioned_amount']) if lr['sanctioned_amount'] > 0 else "—"}
                </div>
                <div style="color:rgba(255,255,255,0.35);font-size:0.7rem">{lr['eligibility_pct']}% of requested</div>
            </div>
            <div style="text-align:center;min-width:120px;">
                <div style="color:rgba(255,255,255,0.4);font-size:0.68rem;letter-spacing:0.1em;text-transform:uppercase">Interest Rate</div>
                <div style="color:{lr_color};font-size:1.5rem;font-weight:700;font-family:'IBM Plex Mono',monospace">{lr['interest_rate']}%</div>
                <div style="color:rgba(255,255,255,0.35);font-size:0.7rem">p.a. (MCLR + spread)</div>
            </div>
            <div style="text-align:center;min-width:100px;">
                <div style="color:rgba(255,255,255,0.4);font-size:0.68rem;letter-spacing:0.1em;text-transform:uppercase">Max Tenure</div>
                <div style="color:{lr_color};font-size:1.5rem;font-weight:700;font-family:'IBM Plex Mono',monospace">{lr['tenure_years']} Yrs</div>
                <div style="color:rgba(255,255,255,0.35);font-size:0.7rem">suggested</div>
            </div>
            <div style="flex:1;min-width:180px;">
                <div style="color:rgba(255,255,255,0.4);font-size:0.68rem;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:4px">Recommendation</div>
                <div style="color:{lr_color};font-size:0.9rem;font-weight:600">{lr['decision_label']}</div>
                <div style="color:rgba(255,255,255,0.35);font-size:0.7rem;margin-top:4px">
                    GST: {d['gst_compliance']}  &nbsp;•&nbsp;  CIBIL: {d['cibil_score']}  &nbsp;•&nbsp;  MCA: {d['mca_status']}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊  Financial Ratios",
        "📈  Risk Dashboard",
        "⚠️  Risk Factors",
        "🔬  Stress Test",
        "📄  CAM Report",
        "🗄️  Portfolio History",
        "🤖  ML Explainability"
    ])

    # ════════════════════════════════════════════════════════════════════
    # TAB 1 — FINANCIAL RATIOS
    # ════════════════════════════════════════════════════════════════════
    with tab1:
        st.markdown('<div class="section-title">Calculated Financial Ratios</div>', unsafe_allow_html=True)

        def ratio_card(label, value, benchmark, good, warn, unit="x"):
            if value is None or value == 0:
                status = "—"; color = "#9ca3af"
            elif value >= good:
                status = "✅ Strong"; color = "#22c55e"
            elif value >= warn:
                status = "🟡 Acceptable"; color = "#f59e0b"
            else:
                status = "🔴 Weak"; color = "#ef4444"
            return f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color:{color}; font-size:1.4rem">{value:.2f}{unit}</div>
                <div class="metric-sub">Benchmark: {benchmark}  &nbsp;•&nbsp;  {status}</div>
            </div>"""

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(ratio_card("DSCR", d["dscr"], "≥ 1.50x", 1.5, 1.2), unsafe_allow_html=True)
        with c2:
            st.markdown(ratio_card("Interest Coverage (ICR)", d["icr"], "≥ 2.50x", 2.5, 1.5) if d["icr"] > 0 else
                        '<div class="metric-card"><div class="metric-label">ICR</div><div class="metric-value" style="color:#9ca3af">N/A</div><div class="metric-sub">Interest expense not provided</div></div>',
                        unsafe_allow_html=True)
        with c3:
            st.markdown(ratio_card("Debt-to-Equity", d["debt_equity"], "≤ 2.00x", 0, 2.0, "x") if True else "",
                        unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        c4, c5, c6 = st.columns(3)
        with c4:
            st.markdown(ratio_card("EBITDA Margin", d["ebitda_margin"], "≥ 15%", 15, 8, "%") if d["ebitda_margin"] > 0 else
                        '<div class="metric-card"><div class="metric-label">EBITDA Margin</div><div class="metric-value" style="color:#9ca3af">N/A</div><div class="metric-sub">EBITDA not provided</div></div>',
                        unsafe_allow_html=True)
        with c5:
            st.markdown(ratio_card("Current Ratio", d["current_ratio"], "≥ 1.33x", 1.33, 1.0) if d["current_ratio"] > 0 else
                        '<div class="metric-card"><div class="metric-label">Current Ratio</div><div class="metric-value" style="color:#9ca3af">N/A</div><div class="metric-sub">Balance sheet data not provided</div></div>',
                        unsafe_allow_html=True)
        with c6:
            rev_g = d["revenue_growth"]
            rg_color = "#22c55e" if rev_g >= 10 else ("#f59e0b" if rev_g >= 0 else "#ef4444")
            rg_status = "✅ Strong" if rev_g >= 10 else ("🟡 Moderate" if rev_g >= 0 else "🔴 Declining")
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Revenue Growth</div>
                <div class="metric-value" style="color:{rg_color}; font-size:1.4rem">{rev_g:.1f}%</div>
                <div class="metric-sub">Benchmark: ≥ 10%  &nbsp;•&nbsp;  {rg_status}</div>
            </div>""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════
    # TAB 2 — RISK DASHBOARD
    # ════════════════════════════════════════════════════════════════════
    with tab2:
        col_gauge, col_radar = st.columns([1, 1])

        # ── Gauge chart ───────────────────────────────────────────────
        with col_gauge:
            st.markdown('<div class="section-title">Overall Risk Score</div>', unsafe_allow_html=True)
            gauge_color = "#ef4444" if d["score"] > 55 else ("#f59e0b" if d["score"] > 28 else "#22c55e")
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=d["score"],
                number={"font": {"size": 42, "color": gauge_color, "family": "IBM Plex Mono"}},
                title={"text": f"<b>{d['category']}</b>",
                       "font": {"size": 14, "color": "#c9974a", "family": "IBM Plex Sans"}},
                gauge={
                    "axis": {"range": [0, 100], "tickfont": {"color": "#6b7280", "size": 10}, "tickwidth": 1},
                    "bar":  {"color": gauge_color, "thickness": 0.28},
                    "bgcolor": "rgba(0,0,0,0)",
                    "borderwidth": 0,
                    "steps": [
                        {"range": [0, 28],   "color": "rgba(34,197,94,0.15)"},
                        {"range": [28, 55],  "color": "rgba(245,158,11,0.15)"},
                        {"range": [55, 100], "color": "rgba(239,68,68,0.15)"},
                    ],
                    "threshold": {"line": {"color": gauge_color, "width": 3}, "value": d["score"]},
                }
            ))
            fig_gauge.update_layout(
                height=280, margin=dict(t=30, b=10, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font={"family": "IBM Plex Sans"}
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

        # ── Radar chart ───────────────────────────────────────────────
        with col_radar:
            st.markdown('<div class="section-title">Risk Component Breakdown</div>', unsafe_allow_html=True)
            categories = ["Capacity", "Capital", "Character", "Conditions"]
            values     = [d["capacity_risk"], d["capital_risk"], d["character_risk"], d["conditions_risk"]]

            fig_radar = go.Figure(go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill="toself",
                fillcolor="rgba(201,151,74,0.18)",
                line=dict(color="#c9974a", width=2),
                marker=dict(color="#c9974a", size=7),
                name="Risk Score"
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100],
                                    color="rgba(255,255,255,0.3)",
                                    gridcolor="rgba(255,255,255,0.08)",
                                    tickfont=dict(color="#6b7280", size=9)),
                    angularaxis=dict(color="rgba(255,255,255,0.6)",
                                     gridcolor="rgba(255,255,255,0.08)"),
                    bgcolor="rgba(0,0,0,0)"
                ),
                showlegend=False,
                height=280, margin=dict(t=20, b=20, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font={"color": "#9ca3af", "family": "IBM Plex Sans"}
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        # ── Weighted bar chart ────────────────────────────────────────
        st.markdown('<div class="section-title">Weighted Score Contribution (5 Cs Model)</div>', unsafe_allow_html=True)

        weights = {"Capacity (35%)": d["capacity_risk"] * 0.35,
                   "Capital (25%)":  d["capital_risk"]  * 0.25,
                   "Character (20%)":d["character_risk"]* 0.20,
                   "Conditions (20%)":d["conditions_risk"]*0.20}

        bar_colors = ["#ef4444" if v > 20 else ("#f59e0b" if v > 10 else "#22c55e")
                      for v in weights.values()]

        fig_bar = go.Figure(go.Bar(
            x=list(weights.keys()),
            y=list(weights.values()),
            marker_color=bar_colors,
            marker_line_width=0,
            text=[f"{v:.1f}" for v in weights.values()],
            textposition="outside",
            textfont=dict(color="white", size=11, family="IBM Plex Mono")
        ))
        fig_bar.update_layout(
            height=280, margin=dict(t=30, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(color="rgba(255,255,255,0.5)", gridcolor="rgba(0,0,0,0)",
                       tickfont=dict(family="IBM Plex Sans", size=11)),
            yaxis=dict(color="rgba(255,255,255,0.3)", gridcolor="rgba(255,255,255,0.06)"),
            font={"family": "IBM Plex Sans"}
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # ── EWS ───────────────────────────────────────────────────────
        st.markdown('<div class="section-title">⚡ Early Warning Signals</div>', unsafe_allow_html=True)
        for sev, msg in d["ews_signals"]:
            if "Critical" in sev:
                st.markdown(f'<div class="ews-critical"><b>{sev}</b> — {msg}</div>', unsafe_allow_html=True)
            elif "Watch" in sev:
                st.markdown(f'<div class="ews-watch"><b>{sev}</b> — {msg}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="ews-clear"><b>{sev}</b> — {msg}</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════
    # TAB 3 — RISK FACTORS
    # ════════════════════════════════════════════════════════════════════
    with tab3:
        col_r, col_p = st.columns(2)
        with col_r:
            st.markdown('<div class="section-title">⚠️ Risk Factors Identified</div>', unsafe_allow_html=True)
            if d["reasons"]:
                for r in d["reasons"]:
                    css = "risk-pill-red" if "🔴" in r or "⛔" in r else "risk-pill-yellow"
                    st.markdown(f'<div class="{css}">{r}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="risk-pill-green">✅ No significant risk factors detected</div>', unsafe_allow_html=True)

        with col_p:
            st.markdown('<div class="section-title">✅ Positive Credit Attributes</div>', unsafe_allow_html=True)
            if d["positives"]:
                for p in d["positives"]:
                    st.markdown(f'<div class="risk-pill-green">{p}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="risk-pill-yellow">🟡 No significant positive signals detected</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════
    # TAB 4 — STRESS TEST
    # ════════════════════════════════════════════════════════════════════
    with tab4:
        st.markdown('<div class="section-title">What-If Scenario Analysis</div>', unsafe_allow_html=True)

        sl1, sl2 = st.columns(2)
        with sl1:
            rev_chg  = st.slider("Revenue Change (%)", -50, 50, 0, key="sim_rev")
        with sl2:
            debt_chg = st.slider("Debt Change (%)", -50, 50, 0, key="sim_dbt")

        if st.button("⚡ Run Stress Scenarios", use_container_width=True):
            scenarios = {
                "Base Case":     (0,        0),
                "Stress -20%":   (-20,      20),
                "Severe -40%":   (-40,      40),
                "Recovery +15%": (15,      -10),
                "Custom":        (rev_chg, debt_chg),
            }

            sim_results = []
            for name, (rc, dc) in scenarios.items():
                sr = d["current_revenue"] * (1 + rc / 100)
                sd = d["total_debt"]      * (1 + dc / 100)

                sdscr, sde, sgr, sicr, sem, scr = calculate_ratios(
                    sr, d["previous_revenue"], d["operating_income"],
                    d["loan_obligation"], sd, d["equity"],
                    d["ebitda"], d["interest_expense"],
                    d["current_assets"], d["current_liabs"]
                )
                ss, scat, sdec, _, _, _, _, _, _, _ = calculate_risk(
                    sdscr, sde, sgr, sicr, sem, scr,
                    d["litigation_level"], d["negative_news"],
                    d["promoter_stake"], d["industry"], d["risk_mode"]
                )
                sim_results.append({
                    "Scenario": name,
                    "Risk Score": ss,
                    "Category":  scat,
                    "Decision":  sdec,
                    "DSCR":      round(sdscr, 2),
                    "D/E":       round(sde, 2),
                })

            # Scenario comparison bar chart
            s_names  = [r["Scenario"] for r in sim_results]
            s_scores = [r["Risk Score"] for r in sim_results]
            s_colors = ["#ef4444" if s > 55 else ("#f59e0b" if s > 28 else "#22c55e") for s in s_scores]

            fig_sim = go.Figure(go.Bar(
                x=s_names, y=s_scores, marker_color=s_colors,
                text=s_scores, textposition="outside",
                textfont=dict(color="white", family="IBM Plex Mono", size=12)
            ))
            fig_sim.add_hline(y=28,  line_dash="dot", line_color="#22c55e",
                              annotation_text="Low/Medium threshold (28)")
            fig_sim.add_hline(y=55,  line_dash="dot", line_color="#f59e0b",
                              annotation_text="Medium/High threshold (55)")
            fig_sim.update_layout(
                height=320, margin=dict(t=40, b=10),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(color="rgba(255,255,255,0.5)", gridcolor="rgba(0,0,0,0)",
                           tickfont=dict(family="IBM Plex Sans")),
                yaxis=dict(range=[0, 110], color="rgba(255,255,255,0.3)",
                           gridcolor="rgba(255,255,255,0.06)", title="Risk Score"),
                font={"family": "IBM Plex Sans"}
            )
            st.plotly_chart(fig_sim, use_container_width=True)

            # Results table
            for r in sim_results:
                cat_color = "#22c55e" if r["Category"] == "Low Risk" else ("#f59e0b" if r["Category"] == "Medium Risk" else "#ef4444")
                st.markdown(f"""
                <div style="display:flex; align-items:center; gap:12px; padding:8px 14px;
                            background:rgba(255,255,255,0.04); border-radius:6px;
                            border-left:3px solid {cat_color}; margin-bottom:5px;">
                    <span style="color:#9ca3af; width:120px; font-size:0.82rem;">{r['Scenario']}</span>
                    <span style="color:{cat_color}; font-weight:700; font-family:'IBM Plex Mono'; width:70px">Score: {r['Risk Score']}</span>
                    <span style="color:{cat_color}; font-size:0.82rem; width:120px">{r['Category']}</span>
                    <span style="color:rgba(255,255,255,0.5); font-size:0.78rem">DSCR: {r['DSCR']}x  |  D/E: {r['D/E']}x</span>
                </div>""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════
    # TAB 5 — CAM REPORT
    # ════════════════════════════════════════════════════════════════════
    with tab5:
        st.markdown('<div class="section-title">Generate Credit Appraisal Memo (CAM)</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:rgba(201,151,74,0.1); border:1px solid rgba(201,151,74,0.3);
                    border-radius:8px; padding:14px 18px; margin-bottom:16px;">
            <span style="color:#c9974a; font-weight:600; font-size:0.85rem;">📄 Bank-Grade PDF Report</span><br>
            <span style="color:rgba(255,255,255,0.5); font-size:0.78rem;">
            Generates a professional Credit Appraisal Memo with executive summary, financial ratio analysis,
            weighted risk scorecard, risk factors, analyst narrative, and formal recommendation.
            </span>
        </div>""", unsafe_allow_html=True)

        if st.button("📄 Generate CAM Report", use_container_width=True):
            with st.spinner("Generating PDF..."):
                filename = f"CAM_{(d['company_name'] or 'Company').replace(' ','_')}.pdf"
                generate_cam(
                    filename,
                    d["company_name"], d["industry"],
                    d["category"], d["decision"],
                    d["score"], d["confidence"],
                    d["dscr"], d["debt_equity"], d["revenue_growth"],
                    d["icr"], d["ebitda_margin"], d["current_ratio"],
                    d["capacity_risk"], d["capital_risk"],
                    d["character_risk"], d["conditions_risk"],
                    d["reasons"], d["positives"],
                    d["risk_mode"], d["loan_amount"]
                )
                with open(filename, "rb") as f:
                    st.download_button(
                        label="⬇️  Download Credit Appraisal Memo (PDF)",
                        data=f,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True
                    )

    # ════════════════════════════════════════════════════════════════════
    # TAB 6 — PORTFOLIO HISTORY
    # ════════════════════════════════════════════════════════════════════
    with tab6:
        st.markdown('<div class="section-title">📊 Portfolio Overview</div>', unsafe_allow_html=True)

        stats = get_portfolio_stats()

        if stats["total"] == 0:
            st.markdown('<div style="color:rgba(255,255,255,0.4);text-align:center;padding:30px">No applications saved yet. Run an analysis first!</div>', unsafe_allow_html=True)
        else:
            # ── Stats Row ────────────────────────────────────────────
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Total Applications", stats["total"])
            c2.metric("🟢 Low Risk",    stats["low"])
            c3.metric("🟡 Medium Risk", stats["medium"])
            c4.metric("🔴 High Risk",   stats["high"])
            c5.metric("Avg Risk Score", f"{stats['avg_score']}/100")

            st.markdown("<br>", unsafe_allow_html=True)

            col_pie, col_bar = st.columns(2)

            # ── Pie chart — Risk distribution ─────────────────────
            with col_pie:
                st.markdown('<div class="section-title">Risk Distribution</div>', unsafe_allow_html=True)
                fig_pie = go.Figure(go.Pie(
                    labels=["Low Risk", "Medium Risk", "High Risk"],
                    values=[stats["low"], stats["medium"], stats["high"]],
                    marker_colors=["#22c55e", "#f59e0b", "#ef4444"],
                    hole=0.5,
                    textfont=dict(family="IBM Plex Sans", size=11),
                ))
                fig_pie.update_layout(
                    height=260, margin=dict(t=20, b=10, l=10, r=10),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    legend=dict(font=dict(color="#9ca3af", family="IBM Plex Sans"), bgcolor="rgba(0,0,0,0)"),
                    font={"family": "IBM Plex Sans"}
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            # ── Exposure bar ──────────────────────────────────────
            with col_bar:
                st.markdown('<div class="section-title">Loan Exposure Summary</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="metric-card" style="margin-bottom:10px">
                    <div class="metric-label">Total Loan Requests</div>
                    <div class="metric-value" style="font-size:1.2rem">₹ {stats['total_exposure']:,.0f}</div>
                </div>
                <div class="metric-card" style="margin-bottom:10px">
                    <div class="metric-label">Total Sanctioned Amount</div>
                    <div class="metric-value" style="font-size:1.2rem;color:#22c55e">₹ {stats['total_sanctioned']:,.0f}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Portfolio Avg DSCR</div>
                    <div class="metric-value" style="font-size:1.2rem;color:#c9974a">{stats['avg_dscr']}x</div>
                </div>
                """, unsafe_allow_html=True)

            # ── Application History Table ─────────────────────────
            st.markdown('<div class="section-title">Application History</div>', unsafe_allow_html=True)
            apps = get_all_applications()

            for app in apps:
                cat_color = "#22c55e" if app["risk_category"] == "Low Risk" else ("#f59e0b" if app["risk_category"] == "Medium Risk" else "#ef4444")
                col_a, col_b = st.columns([5, 1])
                with col_a:
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
                                border-left:3px solid {cat_color};border-radius:6px;
                                padding:10px 16px;margin-bottom:6px;">
                        <span style="color:#ffffff;font-weight:600;font-size:0.9rem">{app['company_name']}</span>
                        <span style="color:#9ca3af;font-size:0.78rem;margin-left:12px">{app['industry']}</span>
                        <span style="color:#9ca3af;font-size:0.78rem;margin-left:12px">{app['created_at']}</span>
                        <br>
                        <span style="color:{cat_color};font-size:0.82rem;font-weight:600">{app['risk_category']}</span>
                        <span style="color:#9ca3af;font-size:0.78rem;margin-left:10px">Score: {app['risk_score']}/100</span>
                        <span style="color:#9ca3af;font-size:0.78rem;margin-left:10px">DSCR: {app['dscr']}x</span>
                        <span style="color:#9ca3af;font-size:0.78rem;margin-left:10px">D/E: {app['debt_equity']}x</span>
                        <span style="color:#9ca3af;font-size:0.78rem;margin-left:10px">Rate: {app['interest_rate']}%</span>
                    </div>
                    """, unsafe_allow_html=True)
                with col_b:
                    if st.button("🗑️", key=f"del_{app['id']}", help="Delete this record"):
                        delete_application(app["id"])
                        st.rerun()

    # ════════════════════════════════════════════════════════════════════
    # TAB 7 — ML EXPLAINABILITY
    # ════════════════════════════════════════════════════════════════════
    with tab7:
        ml = d.get("ml_result")

        if ml is None:
            st.warning("ML model could not run. Check that scikit-learn and shap are installed.")
        else:
            # ── ML vs Rule-Based comparison ───────────────────────────
            st.markdown('<div class="section-title">🤖 ML Model vs Rule-Based Engine</div>', unsafe_allow_html=True)

            ml_color = "#22c55e" if ml["ml_category"] == "Low Risk" else ("#f59e0b" if ml["ml_category"] == "Medium Risk" else "#ef4444")
            rb_color = "#22c55e" if d["category"] == "Low Risk" else ("#f59e0b" if d["category"] == "Medium Risk" else "#ef4444")

            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Rule-Based Engine</div>
                    <div class="metric-value" style="color:{rb_color};font-size:1.2rem">{d['category']}</div>
                    <div class="metric-sub">Score: {d['score']}/100 · Confidence: {d['confidence']}%</div>
                </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">ML Model (Gradient Boosting)</div>
                    <div class="metric-value" style="color:{ml_color};font-size:1.2rem">{ml['ml_category']}</div>
                    <div class="metric-sub">Confidence: {ml['ml_confidence']}%</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Probability bars ──────────────────────────────────────
            st.markdown('<div class="section-title">Prediction Probability Distribution</div>', unsafe_allow_html=True)
            proba = ml["probabilities"]
            fig_proba = go.Figure()
            colors_p = {"Low Risk": "#22c55e", "Medium Risk": "#f59e0b", "High Risk": "#ef4444"}
            for label, pct in proba.items():
                fig_proba.add_trace(go.Bar(
                    name=label, x=[pct], y=["Probability"],
                    orientation="h", marker_color=colors_p[label],
                    text=f"{pct}%", textposition="inside",
                    textfont=dict(color="white", size=12, family="IBM Plex Mono")
                ))
            fig_proba.update_layout(
                barmode="stack", height=120,
                margin=dict(t=10, b=10, l=10, r=10),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                showlegend=True,
                legend=dict(font=dict(color="#9ca3af"), bgcolor="rgba(0,0,0,0)", orientation="h"),
                xaxis=dict(range=[0, 100], color="rgba(255,255,255,0.3)",
                           gridcolor="rgba(255,255,255,0.06)"),
                yaxis=dict(color="rgba(255,255,255,0.3)", gridcolor="rgba(0,0,0,0)"),
                font={"family": "IBM Plex Sans"}
            )
            st.plotly_chart(fig_proba, use_container_width=True)

            # ── SHAP Waterfall chart ───────────────────────────────────
            st.markdown('<div class="section-title">🔍 SHAP — Why Did the Model Decide This?</div>', unsafe_allow_html=True)
            st.markdown('<div style="color:rgba(255,255,255,0.4);font-size:0.78rem;margin-bottom:12px">Each bar shows how much a feature PUSHED the risk score up (red) or down (green)</div>', unsafe_allow_html=True)

            shap_feats = [ml["shap_features"][i] for i in range(min(10, len(ml["shap_features"])))]
            shap_vals  = [ml["shap_values"][i]   for i in range(min(10, len(ml["shap_values"])))]
            raw_vals   = [ml["raw_values"][i]    for i in range(min(10, len(ml["raw_values"])))]

            feat_labels = [f'{FEATURE_LABELS.get(shap_feats[i], shap_feats[i])} = {raw_vals[i]}' for i in range(len(shap_feats))]
            bar_colors_s = ["#ef4444" if v > 0 else "#22c55e" for v in shap_vals]

            fig_shap = go.Figure(go.Bar(
                x=shap_vals, y=feat_labels,
                orientation="h",
                marker_color=bar_colors_s,
                marker_line_width=0,
                text=[f"+{v:.3f}" if v > 0 else f"{v:.3f}" for v in shap_vals],
                textposition="outside",
                textfont=dict(color="white", size=10, family="IBM Plex Mono")
            ))
            fig_shap.add_vline(x=0, line_color="rgba(255,255,255,0.3)", line_width=1)
            fig_shap.update_layout(
                height=380, margin=dict(t=20, b=20, l=20, r=60),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(color="rgba(255,255,255,0.4)", gridcolor="rgba(255,255,255,0.06)",
                           title="SHAP Value (Impact on Risk Score)"),
                yaxis=dict(color="rgba(255,255,255,0.7)", gridcolor="rgba(0,0,0,0)",
                           tickfont=dict(size=9)),
                font={"family": "IBM Plex Sans"}
            )
            st.plotly_chart(fig_shap, use_container_width=True)

            # ── Feature Importance ────────────────────────────────────
            st.markdown('<div class="section-title">📊 Global Feature Importance (Trained Model)</div>', unsafe_allow_html=True)
            fi = get_feature_importance()
            fi_labels = list(fi.keys())[:8]
            fi_vals   = [round(v * 100, 1) for v in list(fi.values())[:8]]

            fig_fi = go.Figure(go.Bar(
                x=fi_vals, y=fi_labels, orientation="h",
                marker_color="#c9974a", marker_line_width=0,
                text=[f"{v}%" for v in fi_vals], textposition="outside",
                textfont=dict(color="white", size=10, family="IBM Plex Mono")
            ))
            fig_fi.update_layout(
                height=320, margin=dict(t=10, b=10, l=20, r=60),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(color="rgba(255,255,255,0.4)", gridcolor="rgba(255,255,255,0.06)"),
                yaxis=dict(color="rgba(255,255,255,0.7)", gridcolor="rgba(0,0,0,0)",
                           tickfont=dict(size=9), autorange="reversed"),
                font={"family": "IBM Plex Sans"}
            )
            st.plotly_chart(fig_fi, use_container_width=True)

            # ── Top Risk Drivers ──────────────────────────────────────
            if ml["top_risk"] or ml["top_positive"]:
                c_risk, c_pos = st.columns(2)
                with c_risk:
                    st.markdown('<div class="section-title">⚠️ Top Risk Drivers (SHAP)</div>', unsafe_allow_html=True)
                    for feat, impact, val in ml["top_risk"]:
                        st.markdown(f'<div class="risk-pill-red">📌 {feat} = {val}  (+{impact} risk)</div>', unsafe_allow_html=True)
                with c_pos:
                    st.markdown('<div class="section-title">✅ Risk Reducers (SHAP)</div>', unsafe_allow_html=True)
                    for feat, impact, val in ml["top_positive"]:
                        st.markdown(f'<div class="risk-pill-green">✅ {feat} = {val}  (-{impact} risk)</div>', unsafe_allow_html=True)

else:
    # ── EMPTY STATE ───────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center; padding:60px 20px;">
        <div style="font-size:3.5rem; margin-bottom:16px">🏦</div>
        <div style="color:rgba(255,255,255,0.6); font-size:1.05rem; margin-bottom:8px">
            Enter company details in the sidebar and click <b style="color:#c9974a">Run Credit Analysis</b>
        </div>
        <div style="color:rgba(255,255,255,0.3); font-size:0.82rem">
            6 Financial Ratios  •  4-Component Risk Model  •  Early Warning Signals  •  Stress Testing  •  CAM PDF
        </div>
    </div>
    """, unsafe_allow_html=True)