"""
Intelli-Credit: AI-Powered Corporate Credit Decision Engine
v3.4 STABLE — Clean, tested, production ready
"""

import streamlit as st
import plotly.graph_objects as go
import re
import io
from research_agent import run_research_agent
from risk_engine import (
    calculate_ratios, calculate_risk, analyze_primary_notes,
    get_ews_signals, recommend_loan, INDUSTRY_RISK_MAP
)
from cam_generator import generate_cam
from database import save_application, get_all_applications, get_portfolio_stats, delete_application
from ml_engine import ml_predict, get_feature_importance, FEATURE_LABELS

st.set_page_config(
    page_title="Intelli-Credit | Corporate Credit Engine",
    page_icon="🏦", layout="wide", initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');
html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
.stApp { background: #030d1a; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #041120 0%, #071929 100%); border-right: 1px solid rgba(201,151,74,0.25); }
[data-testid="stSidebar"] .stMarkdown h3 { color: #c9974a !important; font-size: 0.78rem !important; letter-spacing: 0.12em; text-transform: uppercase; }
.main-header { background: linear-gradient(135deg, #0d2137 0%, #0a1929 60%, #112240 100%); border: 1px solid rgba(201,151,74,0.35); border-radius: 12px; padding: 28px 36px; margin-bottom: 28px; }
.main-header h1 { color: #ffffff; font-size: 2rem; font-weight: 700; margin: 0 0 4px 0; }
.main-header p { color: rgba(255,255,255,0.55); font-size: 0.9rem; margin: 0; }
.header-badge { display: inline-block; background: rgba(201,151,74,0.18); color: #c9974a; border: 1px solid rgba(201,151,74,0.4); border-radius: 20px; padding: 3px 12px; font-size: 0.72rem; font-weight: 600; letter-spacing: 0.08em; margin-bottom: 10px; }
.section-title { color: #c9974a; font-size: 0.72rem; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase; margin-bottom: 16px; border-bottom: 1px solid rgba(201,151,74,0.2); padding-bottom: 8px; }
.metric-card { background: rgba(13,33,55,0.7); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 14px 16px; text-align: center; }
.metric-label { color: rgba(255,255,255,0.45); font-size: 0.7rem; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 6px; }
.metric-value { color: #ffffff; font-size: 1.6rem; font-weight: 700; font-family: 'IBM Plex Mono', monospace; line-height: 1; }
.metric-sub { color: rgba(255,255,255,0.35); font-size: 0.7rem; margin-top: 4px; }
.decision-low    { background: linear-gradient(135deg, rgba(16,85,50,0.4), rgba(5,46,22,0.6));   border: 1.5px solid rgba(34,197,94,0.5);  border-radius: 10px; padding: 20px 24px; text-align: center; }
.decision-medium { background: linear-gradient(135deg, rgba(120,53,15,0.4), rgba(92,45,10,0.6)); border: 1.5px solid rgba(245,158,11,0.5); border-radius: 10px; padding: 20px 24px; text-align: center; }
.decision-high   { background: linear-gradient(135deg, rgba(127,29,29,0.4), rgba(69,10,10,0.6)); border: 1.5px solid rgba(239,68,68,0.5);  border-radius: 10px; padding: 20px 24px; text-align: center; }
.decision-title  { font-size: 1.5rem; font-weight: 700; margin-bottom: 4px; }
.decision-sub    { font-size: 0.85rem; opacity: 0.7; }
.risk-pill-red    { display: inline-block; background: rgba(127,29,29,0.3);  border: 1px solid rgba(239,68,68,0.4);  color: #fca5a5; border-radius: 20px; padding: 5px 12px; font-size: 0.8rem; margin: 3px 2px; }
.risk-pill-yellow { display: inline-block; background: rgba(120,53,15,0.3);  border: 1px solid rgba(245,158,11,0.4); color: #fde68a; border-radius: 20px; padding: 5px 12px; font-size: 0.8rem; margin: 3px 2px; }
.risk-pill-green  { display: inline-block; background: rgba(5,46,22,0.4);    border: 1px solid rgba(34,197,94,0.4);  color: #86efac; border-radius: 20px; padding: 5px 12px; font-size: 0.8rem; margin: 3px 2px; }
.ews-critical { background: rgba(127,29,29,0.25); border-left: 3px solid #ef4444; border-radius: 0 6px 6px 0; padding: 8px 14px; margin: 5px 0; color: #fca5a5; font-size: 0.82rem; }
.ews-watch    { background: rgba(120,53,15,0.25);  border-left: 3px solid #f59e0b; border-radius: 0 6px 6px 0; padding: 8px 14px; margin: 5px 0; color: #fde68a; font-size: 0.82rem; }
.ews-clear    { background: rgba(5,46,22,0.25);    border-left: 3px solid #22c55e; border-radius: 0 6px 6px 0; padding: 8px 14px; margin: 5px 0; color: #86efac; font-size: 0.82rem; }
.stButton > button { background: linear-gradient(135deg, #c9974a, #b07d35); color: #000000; font-weight: 700; border: none; border-radius: 8px; padding: 0.55rem 1.5rem; font-size: 0.9rem; width: 100%; }
div[data-testid="stMetricValue"] { color: #ffffff !important; }
div[data-testid="stMetricLabel"] { color: rgba(255,255,255,0.5) !important; font-size: 0.72rem !important; }
.stNumberInput label, .stTextInput label, .stSelectbox label, .stTextArea label, .stSlider label { color: rgba(255,255,255,0.65) !important; font-size: 0.78rem !important; font-weight: 500; }
input, textarea, select { background: rgba(255,255,255,0.05) !important; color: #ffffff !important; border-color: rgba(255,255,255,0.15) !important; }
.stDownloadButton > button { background: linear-gradient(135deg, #1a4a6e, #0f3050) !important; color: #ffffff !important; border: 1px solid rgba(255,255,255,0.2) !important; }
.stTabs [data-baseweb="tab"] { color: rgba(255,255,255,0.5); font-size: 0.82rem; font-weight: 500; }
.stTabs [aria-selected="true"] { color: #c9974a !important; border-bottom-color: #c9974a !important; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #030d1a; }
::-webkit-scrollbar-thumb { background: rgba(201,151,74,0.4); border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DEMO DATA
# ══════════════════════════════════════════════════════════════════════════════
DEMO = {
    "company_name": "Apex Textiles Ltd", "industry": "Textiles",
    "loan_amount": 5000000.0, "risk_mode": "Balanced",
    "current_revenue": 50000000.0, "previous_revenue": 42000000.0,
    "ebitda": 8000000.0, "operating_income": 6500000.0,
    "interest_expense": 2000000.0, "total_debt": 25000000.0,
    "equity": 12000000.0, "current_assets": 18000000.0,
    "current_liabs": 14000000.0, "loan_obligation": 4000000.0,
    "promoter_stake": 45, "litigation_level": "Medium", "negative_news": 3,
    "gst_compliance": "Regular & Compliant", "cibil_score": 6.5,
    "mca_status": "Up to Date",
}

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
for key, default in [
    ("analysis_done", False), ("demo_loaded", False),
    ("pdf_data", {}), ("pdf_notes", ""), ("pdf_name", ""),
    ("onboarding_done", False), ("onboarding_step", 1),
    ("entity_data", {}), ("loan_data", {}),
    ("docs", {}),  # 5 document types storage
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ══════════════════════════════════════════════════════════════════════════════
# PDF PARSER
# ══════════════════════════════════════════════════════════════════════════════
def parse_pdf(pdf_bytes):
    """
    PDF se financial data extract karo.
    Conservative — sirf confirmed values fill karo, baaki blank.
    """
    result = {}
    try:
        # ── Text extract karo ──────────────────────────────────────────────
        try:
            import pdfplumber
            lines = []
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                total = len(pdf.pages)
                for i, page in enumerate(pdf.pages):
                    txt = page.extract_text() or ""
                    lines.append(txt)
                    # Tables sirf last 60% pages se (financial statements)
                    if i >= int(total * 0.4):
                        try:
                            for tbl in (page.extract_tables() or []):
                                for row in (tbl or []):
                                    if row:
                                        lines.append(" | ".join(
                                            str(c).strip() if c else "" for c in row
                                        ))
                        except:
                            pass
            raw = "\n".join(lines)
        except ImportError:
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            raw = "\n".join(p.extract_text() or "" for p in reader.pages)

        result["_raw"]   = raw[:3000]
        result["_pages"] = len(raw.split("\n"))
        raw_low = raw.lower()

        # ── Number helpers ──────────────────────────────────────────────────
        def to_rs(s):
            """String to float"""
            try:
                return float(str(s).replace(",", "").replace(" ", "").strip())
            except:
                return None

        def crore(s):
            """Crore string to rupees"""
            v = to_rs(s)
            return v * 10_000_000 if v and v > 0 else None

        def find_crore(patterns):
            """'keyword ... X crore/cr' pattern dhundho"""
            for pat in patterns:
                matches = re.findall(pat, raw, re.IGNORECASE)
                for m in matches:
                    v = crore(m)
                    if v and v > 0:
                        return v
            return None

        def find_num(patterns, min_v=0, max_v=1e13):
            """'keyword | X' table pattern dhundho"""
            for pat in patterns:
                matches = re.findall(pat, raw, re.IGNORECASE)
                for m in matches:
                    v = to_rs(m)
                    if v and min_v < v < max_v:
                        return v
            return None

        # ── REVENUE ──────────────────────────────────────────────────────────
        rev = find_crore([
            r"revenue(?:\s+of)?(?:\s+INR)?[^\d]{0,40}([\d,]+(?:\.\d+)?)\s*cr(?:ore)?",
            r"revenue from operations[^\d]{0,30}([\d,]+(?:\.\d+)?)\s*cr(?:ore)?",
            r"total revenue[^\d]{0,30}([\d,]+(?:\.\d+)?)\s*cr(?:ore)?",
            r"turnover[^\d]{0,30}([\d,]+(?:\.\d+)?)\s*cr(?:ore)?",
            r"total income[^\d]{0,30}([\d,]+(?:\.\d+)?)\s*cr(?:ore)?",
        ])
        if not rev:
            rev = find_num([
                r"revenue from operations[\s\|]{0,10}([\d,]{6,})",
                r"total revenue[\s\|]{0,10}([\d,]{7,})",
                r"total income[\s\|]{0,10}([\d,]{7,})",
            ], min_v=1_000_000)
        if rev:
            result["current_revenue"] = rev
            # Previous year — dusri occurrence
            all_r = re.findall(
                r"revenue(?:\s+of)?(?:\s+INR)?[^\d]{0,40}([\d,]+(?:\.\d+)?)\s*cr(?:ore)?",
                raw, re.IGNORECASE
            )
            prev_vals = [crore(x) for x in all_r if crore(x) and abs(crore(x) - rev) > 1000]
            if prev_vals:
                result["previous_revenue"] = prev_vals[0]

        # ── EBITDA ────────────────────────────────────────────────────────────
        ebitda = find_crore([
            r"ebitda[^\d]{0,30}([\d,]+(?:\.\d+)?)\s*cr(?:ore)?",
            r"earnings before interest[^\d]{0,50}([\d,]+(?:\.\d+)?)\s*cr(?:ore)?",
        ])
        if not ebitda:
            ebitda = find_num([
                r"ebitda[\s\|]{0,10}([\d,]{4,})",
                r"earnings before interest[\s\|]{0,30}([\d,]{5,})",
            ], min_v=10_000)
        if ebitda:
            result["ebitda"] = ebitda

        # ── PAT / NET PROFIT ──────────────────────────────────────────────────
        pat = find_crore([
            r"profit after tax[^\d]{0,30}([\d,]+(?:\.\d+)?)\s*cr(?:ore)?",
            r"\bpat(?:\s+of)?(?:\s+INR)?[^\d]{0,20}([\d,]+(?:\.\d+)?)\s*cr(?:ore)?",
            r"net profit[^\d]{0,30}([\d,]+(?:\.\d+)?)\s*cr(?:ore)?",
            r"profit for the year[^\d]{0,30}([\d,]+(?:\.\d+)?)\s*cr(?:ore)?",
        ])
        if not pat:
            pat = find_num([
                r"profit after tax[\s\|]{0,10}([\d,]{4,})",
                r"profit for the year[\s\|]{0,10}([\d,]{4,})",
                r"net profit[\s\|]{0,10}([\d,]{4,})",
            ], min_v=10_000)
        if pat:
            result["operating_income"] = pat

        # ── INTEREST / FINANCE COSTS ──────────────────────────────────────────
        interest = find_crore([
            r"finance costs?[^\d]{0,30}([\d,]+(?:\.\d+)?)\s*cr(?:ore)?",
            r"interest expense[^\d]{0,30}([\d,]+(?:\.\d+)?)\s*cr(?:ore)?",
            r"interest.*?borrowing[^\d]{0,30}([\d,]+(?:\.\d+)?)\s*cr(?:ore)?",
        ])
        if not interest:
            interest = find_num([
                r"finance costs?[\s\|]{0,10}([\d,]{4,})",
                r"interest expense[\s\|]{0,10}([\d,]{4,})",
                r"finance charges[\s\|]{0,10}([\d,]{4,})",
            ], min_v=1_000, max_v=500_000_000)
        if interest:
            result["interest_expense"] = interest

        # ── TOTAL DEBT ────────────────────────────────────────────────────────
        debt = find_crore([
            r"total borrowings?[^\d]{0,30}([\d,]+(?:\.\d+)?)\s*cr(?:ore)?",
            r"total debt[^\d]{0,30}([\d,]+(?:\.\d+)?)\s*cr(?:ore)?",
            r"raised.*?INR\s*([\d,]+(?:\.\d+)?)\s*cr(?:ore)?.*?debt",
            r"borrowings?[^\d]{0,20}([\d,]+(?:\.\d+)?)\s*cr(?:ore)?",
        ])
        if not debt:
            debt = find_num([
                r"total borrowings?[\s\|]{0,10}([\d,]{6,})",
                r"total debt[\s\|]{0,10}([\d,]{6,})",
            ], min_v=100_000)
        if debt:
            result["total_debt"] = debt

        # ── EQUITY ────────────────────────────────────────────────────────────
        equity = find_crore([
            r"total equity[^\d]{0,30}([\d,]+(?:\.\d+)?)\s*cr(?:ore)?",
            r"net worth[^\d]{0,30}([\d,]+(?:\.\d+)?)\s*cr(?:ore)?",
            r"shareholders.{0,5}equity[^\d]{0,30}([\d,]+(?:\.\d+)?)\s*cr(?:ore)?",
        ])
        if not equity:
            equity = find_num([
                r"total equity[\s\|]{0,10}([\d,]{5,})",
                r"net worth[\s\|]{0,10}([\d,]{5,})",
                r"shareholders.{0,5}equity[\s\|]{0,10}([\d,]{5,})",
            ], min_v=10_000)
        if equity:
            result["equity"] = equity

        # ── CURRENT ASSETS ────────────────────────────────────────────────────
        ca = find_num([
            r"total current assets[\s\|]{0,10}([\d,]{5,})",
            r"current assets[\s\|]{0,10}([\d,]{5,})",
        ], min_v=10_000)
        if not ca:
            ca = find_crore([
                r"total assets[^\d]{0,30}([\d,]+(?:\.\d+)?)\s*cr(?:ore)?",
            ])
        if ca:
            result["current_assets"] = ca

        # ── CURRENT LIABILITIES ───────────────────────────────────────────────
        cl = find_num([
            r"total current liabilities[\s\|]{0,10}([\d,]{5,})",
            r"current liabilities[\s\|]{0,10}([\d,]{5,})",
        ], min_v=10_000)
        if cl:
            result["current_liabs"] = cl

        # ── ANNUAL REPAYMENT ──────────────────────────────────────────────────
        rep = find_num([
            r"annual repayment[\s\|]{0,10}([\d,]{5,})",
            r"debt repayment[\s\|]{0,10}([\d,]{5,})",
        ], min_v=10_000)
        if rep:
            result["loan_obligation"] = rep

        # ── COMPANY NAME ──────────────────────────────────────────────────────
        for pat in [
            r"About\s+([A-Z][a-zA-Z\s&\.]{4,40}(?:Capital|Finance|Limited|Ltd\.?))",
            r"^([A-Z][a-zA-Z\s&\.]{4,40}(?:Capital|Finance|Limited|Ltd\.))\s*$",
        ]:
            m = re.search(pat, raw, re.MULTILINE)
            if m:
                name = m.group(1).strip()
                if 5 < len(name) < 60:
                    result["company_name"] = name
                    break

        # ── CIBIL ─────────────────────────────────────────────────────────────
        cm = re.search(r"cibil[^\d]{0,10}([\d\.]+)\s*/\s*10", raw, re.IGNORECASE)
        if cm:
            vv = float(cm.group(1))
            if 1 <= vv <= 10:
                result["cibil_score"] = vv

        # ── GST ───────────────────────────────────────────────────────────────
        if any(x in raw_low for x in ["regular & compliant", "gst compliant", "filed on time"]):
            result["gst_compliance"] = "Regular & Compliant"
        elif "gst" in raw_low and "minor delay" in raw_low:
            result["gst_compliance"] = "Minor Delays"

        # ── MCA ───────────────────────────────────────────────────────────────
        if "up to date" in raw_low and any(x in raw_low for x in ["mca", "roc", "annual return"]):
            result["mca_status"] = "Up to Date"

        return result

    except Exception as e:
        return {"_error": str(e)}


# ══════════════════════════════════════════════════════════════════════════════
# VALUE RESOLVER — PDF > Demo > Default
# ══════════════════════════════════════════════════════════════════════════════
def v(key, default):
    if key in st.session_state.pdf_data:
        return st.session_state.pdf_data[key]
    if st.session_state.demo_loaded:
        return DEMO.get(key, default)
    return default



# ══════════════════════════════════════════════════════════════════════════════
# SWOT GENERATOR — Rule-based, no API key needed
# ══════════════════════════════════════════════════════════════════════════════
def generate_swot(d):
    """
    Generate SWOT from financial ratios + risk data.
    Returns dict with strengths, weaknesses, opportunities, threats lists.
    """
    strengths     = []
    weaknesses    = []
    opportunities = []
    threats       = []

    # ── STRENGTHS ─────────────────────────────────────────────────────────────
    if d.get("dscr", 0) >= 1.5:
        strengths.append(f"Strong Debt Service Coverage — DSCR {d['dscr']:.2f}x (benchmark ≥ 1.5x) indicates comfortable loan repayment capacity")
    if d.get("revenue_growth", 0) >= 10:
        strengths.append(f"Healthy Revenue Growth — {d['revenue_growth']:.1f}% YoY growth demonstrates strong business momentum")
    if d.get("ebitda_margin", 0) >= 15:
        strengths.append(f"Strong Profitability — EBITDA Margin {d['ebitda_margin']:.1f}% reflects efficient operations")
    if d.get("current_ratio", 0) >= 1.33:
        strengths.append(f"Adequate Liquidity — Current Ratio {d['current_ratio']:.2f}x ensures short-term obligations can be met")
    if d.get("icr", 0) >= 2.5:
        strengths.append(f"Comfortable Interest Coverage — ICR {d['icr']:.2f}x shows earnings well above interest obligations")
    if d.get("promoter_stake", 0) >= 51:
        strengths.append(f"Strong Promoter Commitment — {d['promoter_stake']}% equity stake shows high skin-in-the-game")
    if d.get("gst_compliance") == "Regular & Compliant":
        strengths.append("GST Compliance — Regular & timely filings indicate transparent revenue reporting")
    if d.get("cibil_score", 0) >= 7.5:
        strengths.append(f"Strong Credit History — CIBIL Commercial Score {d['cibil_score']}/10 reflects reliable repayment track record")
    if d.get("debt_equity", 0) <= 1.5 and d.get("debt_equity", 0) > 0:
        strengths.append(f"Conservative Leverage — D/E ratio {d['debt_equity']:.2f}x indicates prudent debt management")
    if not strengths:
        strengths.append("Business has established operations with existing customer base")

    # ── WEAKNESSES ────────────────────────────────────────────────────────────
    if d.get("dscr", 0) < 1.2 and d.get("dscr", 0) > 0:
        weaknesses.append(f"Thin Debt Coverage — DSCR {d['dscr']:.2f}x is below acceptable threshold, indicating repayment stress risk")
    if d.get("debt_equity", 0) > 2.5:
        weaknesses.append(f"High Leverage — D/E ratio {d['debt_equity']:.2f}x significantly above benchmark of 2.0x, increasing financial risk")
    if d.get("ebitda_margin", 0) < 10 and d.get("ebitda_margin", 0) > 0:
        weaknesses.append(f"Thin Margins — EBITDA Margin {d['ebitda_margin']:.1f}% leaves little buffer for adverse conditions")
    if d.get("current_ratio", 0) < 1.0 and d.get("current_ratio", 0) > 0:
        weaknesses.append(f"Liquidity Concern — Current Ratio {d['current_ratio']:.2f}x below 1.0x indicates potential short-term payment difficulty")
    if d.get("revenue_growth", 0) < 0:
        weaknesses.append(f"Declining Revenue — {d['revenue_growth']:.1f}% YoY decline raises sustainability concerns")
    if d.get("promoter_stake", 0) < 40:
        weaknesses.append(f"Low Promoter Stake — {d['promoter_stake']}% raises concerns about management commitment")
    if d.get("cibil_score", 0) < 6 and d.get("cibil_score", 0) > 0:
        weaknesses.append(f"Below-Average Credit Score — CIBIL {d['cibil_score']}/10 indicates past repayment issues")
    if d.get("gst_compliance") in ["Minor Delays", "Frequent Defaults"]:
        weaknesses.append(f"GST Compliance Issues — {d['gst_compliance']} may indicate revenue underreporting or cash flow stress")
    if d.get("icr", 0) < 1.5 and d.get("icr", 0) > 0:
        weaknesses.append(f"Weak Interest Coverage — ICR {d['icr']:.2f}x indicates earnings barely cover interest payments")
    if not weaknesses:
        weaknesses.append("Limited financial history available for comprehensive assessment")

    # ── OPPORTUNITIES ─────────────────────────────────────────────────────────
    industry = d.get("industry", "")
    opportunities.append(f"India's GDP growing at 6.5%+ — creates favorable macro environment for {industry} sector expansion")
    opportunities.append("RBI's focus on MSME credit access presents opportunities for refinancing at better rates")

    if industry in ["Textiles", "Manufacturing", "Steel & Manufacturing"]:
        opportunities.append("PLI (Production Linked Incentive) scheme for manufacturing offers government-backed growth subsidies")
        opportunities.append("China+1 strategy driving global sourcing shift to India — export potential rising")
    elif industry in ["Pharmaceuticals", "Healthcare"]:
        opportunities.append("India's pharmaceutical exports growing 12%+ annually — strong global demand for generic drugs")
        opportunities.append("Digital health and API manufacturing opportunities under Atmanirbhar Bharat")
    elif industry in ["IT / Technology"]:
        opportunities.append("Digital India initiative driving technology adoption across sectors")
        opportunities.append("Global tech outsourcing to India expected to grow 15%+ over next 3 years")
    elif industry in ["Real Estate"]:
        opportunities.append("PMAY (Pradhan Mantri Awas Yojana) driving affordable housing demand")
        opportunities.append("RERA compliance building buyer confidence and sector formalization")
    elif industry in ["NBFC / Financial Services"]:
        opportunities.append("India's credit penetration remains low — large underserved MSME market")
        opportunities.append("Co-lending partnerships with banks offer lower cost of funds")
    else:
        opportunities.append("Growing domestic consumption market presents revenue expansion opportunities")
        opportunities.append("Formalization of economy post-GST creating level playing field")

    if d.get("revenue_growth", 0) >= 15:
        opportunities.append("Strong growth trajectory positions company well for capacity expansion and market share gain")

    # ── THREATS ───────────────────────────────────────────────────────────────
    threats.append("Rising interest rates globally may increase cost of borrowing and reduce debt serviceability")
    threats.append("Rupee depreciation risk may impact import-dependent businesses and input costs")

    if d.get("negative_news", 0) >= 3:
        threats.append(f"{d['negative_news']} negative news articles detected — reputational risk may impact business relationships")
    if d.get("litigation_level") in ["Medium", "High"]:
        threats.append(f"{d['litigation_level']} litigation exposure — pending legal proceedings could result in financial liability")
    if d.get("debt_equity", 0) > 3:
        threats.append("High leverage makes company vulnerable to interest rate hikes and credit tightening")
    if d.get("mca_status") in ["Minor Delays", "Significant Gaps"]:
        threats.append(f"MCA/ROC filing delays — regulatory scrutiny risk and potential penalties")

    if industry in ["Real Estate"]:
        threats.append("Real estate sector faces regulatory uncertainty — RERA compliance requirements and project delay risks")
    elif industry in ["Textiles", "Manufacturing"]:
        threats.append("Raw material price volatility and global supply chain disruptions may compress margins")
    elif industry in ["Pharmaceuticals"]:
        threats.append("US FDA regulatory actions and drug pricing pressure in key export markets")
    elif industry in ["NBFC / Financial Services"]:
        threats.append("RBI regulatory tightening on NBFC sector — increased provisioning norms may impact profitability")

    threats.append("Competition from organized/listed players with access to cheaper capital")

    return {
        "strengths":     strengths[:5],
        "weaknesses":    weaknesses[:5],
        "opportunities": opportunities[:4],
        "threats":       threats[:4],
    }


# ══════════════════════════════════════════════════════════════════════════════
# AUTO DOCUMENT CLASSIFIER
# ══════════════════════════════════════════════════════════════════════════════
DOC_TYPES = {
    "Annual Report":         {"emoji": "📋", "color": "#c9974a", "keywords": ["revenue from operations","profit after tax","balance sheet","ebitda","total equity","cash flow","auditor","annual report","p&l","profit and loss"]},
    "ALM Document":          {"emoji": "⚖️",  "color": "#60a5fa", "keywords": ["asset liability","alm","maturity profile","gap analysis","liquidity","npa","net interest margin","cost of funds","asset quality"]},
    "Shareholding Pattern":  {"emoji": "👥", "color": "#a78bfa", "keywords": ["shareholding","promoter","public holding","fii","dii","mutual fund","demat","shares","equity shareholding","category"]},
    "Borrowing Profile":     {"emoji": "🏦", "color": "#34d399", "keywords": ["borrowing","lender","debenture","ncds","ecb","term loan","working capital","credit facility","sanction","disbursement","outstanding loan"]},
    "Portfolio Performance": {"emoji": "📈", "color": "#fb923c", "keywords": ["portfolio","aum","disbursement","collection efficiency","par","dpd","npa ratio","write off","sector","geography","vintage"]},
}

def classify_document(text):
    """Auto-detect document type from text content"""
    text_low = text.lower()
    scores = {}
    for doc_type, info in DOC_TYPES.items():
        score = sum(1 for kw in info["keywords"] if kw in text_low)
        scores[doc_type] = score
    best = max(scores, key=scores.get)
    confidence = min(100, int((scores[best] / len(DOC_TYPES[best]["keywords"])) * 100))
    return best, confidence, scores



# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:

    # ── Demo Button ───────────────────────────────────────────────────────────
    st.markdown('<div style="background:linear-gradient(135deg,rgba(201,151,74,0.15),rgba(201,151,74,0.05));border:1px solid rgba(201,151,74,0.4);border-radius:8px;padding:8px 12px;margin-bottom:10px;text-align:center;"><span style="color:#c9974a;font-weight:700;font-size:0.8rem">🎯 HACKATHON DEMO</span></div>', unsafe_allow_html=True)

    if st.button("⚡  Load Demo Data — Apex Textiles Ltd", use_container_width=True):
        st.session_state.demo_loaded     = True
        st.session_state.pdf_data        = {}
        st.session_state.pdf_name        = ""
        st.session_state.onboarding_done = True
        st.session_state.entity_data     = {"company_name": "Apex Textiles Ltd", "industry": "Textiles"}
        st.session_state.loan_data       = {"loan_type": "Term Loan", "amount": 5000000}
        st.rerun()

    if st.button("🔄  New Application", use_container_width=True):
        for k in ["onboarding_done","onboarding_step","entity_data","loan_data",
                  "analysis_done","demo_loaded","pdf_data","pdf_name","pdf_notes"]:
            if k == "onboarding_step":
                st.session_state[k] = 1
            elif k in ["entity_data","loan_data","pdf_data"]:
                st.session_state[k] = {}
            elif k == "pdf_notes":
                st.session_state[k] = ""
            else:
                st.session_state[k] = False
        st.rerun()

    st.markdown("---")

    # ── INJECT PDF/DEMO VALUES INTO SESSION STATE (fixes Streamlit value= issue) ──
    field_keys = {
        "inp_revenue":  "current_revenue",
        "inp_prevrev":  "previous_revenue",
        "inp_ebitda":   "ebitda",
        "inp_opincome": "operating_income",
        "inp_interest": "interest_expense",
        "inp_debt":     "total_debt",
        "inp_equity":   "equity",
        "inp_cassets":  "current_assets",
        "inp_cliabs":   "current_liabs",
        "inp_loanob":   "loan_obligation",
        "inp_loanamt":  "loan_amount",
        "inp_cibil":    "cibil_score",
        "inp_promo":    "promoter_stake",
        "inp_negnews":  "negative_news",
    }
    for widget_key, data_key in field_keys.items():
        val_ = v(data_key, None)
        if val_ is not None:
            st.session_state[widget_key] = float(val_)

    st.markdown("### 🏢 Company Profile")

    # Use onboarding data if available
    _ob_company  = st.session_state.entity_data.get("company_name", "")
    _ob_industry = st.session_state.entity_data.get("industry", "")

    company_name = st.text_input("Company Name",
        value=_ob_company if _ob_company else v("company_name", ""),
        placeholder="e.g. Acme Industries Ltd.")

    industry_list = list(INDUSTRY_RISK_MAP.keys())
    _ind = _ob_industry if _ob_industry else v("industry", industry_list[0])
    industry = st.selectbox("Industry Sector", industry_list,
        index=industry_list.index(_ind) if _ind in industry_list else 0)

    loan_amount = st.number_input("Loan Amount Requested (₹)",
        min_value=0.0, step=100000.0, format="%.0f",
        key="inp_loanamt")

    _rm = v("risk_mode", "Balanced")
    risk_mode = st.selectbox("Assessment Mode",
        ["Balanced", "Conservative", "Aggressive"],
        index=["Balanced","Conservative","Aggressive"].index(_rm)
              if _rm in ["Balanced","Conservative","Aggressive"] else 0)

    st.markdown("---")
    st.markdown("### 📊 Financials — P&L")
    current_revenue  = st.number_input("Current Year Revenue (₹)",   min_value=0.0, step=100000.0, format="%.0f", key="inp_revenue")
    previous_revenue = st.number_input("Previous Year Revenue (₹)",  min_value=0.0, step=100000.0, format="%.0f", key="inp_prevrev")
    ebitda           = st.number_input("EBITDA (₹)",                  min_value=0.0, step=100000.0, format="%.0f", key="inp_ebitda")
    operating_income = st.number_input("Operating Income / PAT (₹)", min_value=0.0, step=100000.0, format="%.0f", key="inp_opincome")
    interest_expense = st.number_input("Interest Expense (₹)",       min_value=0.0, step=10000.0,  format="%.0f", key="inp_interest")

    st.markdown("### 🏦 Financials — Balance Sheet")
    total_debt      = st.number_input("Total Debt (₹)",            min_value=0.0, step=100000.0, format="%.0f", key="inp_debt")
    equity          = st.number_input("Total Equity (₹)",          min_value=0.0, step=100000.0, format="%.0f", key="inp_equity")
    current_assets  = st.number_input("Current Assets (₹)",        min_value=0.0, step=100000.0, format="%.0f", key="inp_cassets")
    current_liabs   = st.number_input("Current Liabilities (₹)",   min_value=0.0, step=100000.0, format="%.0f", key="inp_cliabs")
    loan_obligation = st.number_input("Annual Debt Repayment (₹)", min_value=0.0, step=10000.0,  format="%.0f", key="inp_loanob")

    st.markdown("### ⚖️ Qualitative Factors")
    promoter_stake   = st.slider("Promoter Equity Stake (%)", 0, 100, key="inp_promo")
    lit_options      = ["Low","Medium","High"]
    litigation_level = st.selectbox("Litigation Exposure", lit_options,
        index=lit_options.index(v("litigation_level","Low")))
    negative_news    = st.number_input("Negative News Count", min_value=0, step=1,
        key="inp_negnews")
    primary_notes    = st.text_area("Credit Officer Notes",
        placeholder="Enter due-diligence observations...", height=80)

    st.markdown("### 🇮🇳 Indian Context")
    gst_options    = ["Regular & Compliant","Minor Delays","Frequent Defaults","Not Registered"]
    gst_compliance = st.selectbox("GST Filing Compliance", gst_options,
        index=gst_options.index(v("gst_compliance","Regular & Compliant")))
    cibil_score    = st.number_input("CIBIL Commercial Score (1–10)",
        min_value=0.0, max_value=10.0, step=0.1,
        key="inp_cibil")
    mca_options  = ["Up to Date","Minor Delays","Significant Gaps","Not Filed"]
    mca_status   = st.selectbox("MCA21 / ROC Filing Status", mca_options,
        index=mca_options.index(v("mca_status","Up to Date")))

    # ── 5 Document Types Upload ───────────────────────────────────────────────
    st.markdown("### 📁 Document Upload")
    st.caption("Upload karo — AI automatically classify karega aur data extract karega!")

    for doc_type, info in DOC_TYPES.items():
        existing = st.session_state.docs.get(doc_type, {})
        status = "✅" if existing.get("uploaded") else "⬜"
        label = f"{info['emoji']} {doc_type}"

        with st.expander(f"{status} {label}", expanded=False):
            uploaded = st.file_uploader(
                f"Upload {doc_type}",
                type=["pdf","xlsx","xls","csv"],
                key=f"doc_{doc_type.replace(' ','_')}"
            )

            if uploaded:
                # Check if new file
                if uploaded.name != existing.get("filename",""):
                    with st.spinner(f"📄 Processing {doc_type}..."):
                        try:
                            raw_bytes = uploaded.read()
                            # Extract text for classification + parsing
                            if uploaded.name.endswith(".pdf"):
                                try:
                                    import pdfplumber
                                    lines = []
                                    with pdfplumber.open(io.BytesIO(raw_bytes)) as pdf:
                                        for page in pdf.pages:
                                            lines.append(page.extract_text() or "")
                                    raw_text = "\n".join(lines)
                                except:
                                    import PyPDF2
                                    reader = PyPDF2.PdfReader(io.BytesIO(raw_bytes))
                                    raw_text = "\n".join(p.extract_text() or "" for p in reader.pages)
                            else:
                                raw_text = f"Excel/CSV file: {uploaded.name}"

                            # Auto classify
                            detected_type, confidence, scores = classify_document(raw_text)

                        except Exception as e:
                            raw_text = ""
                            detected_type = doc_type
                            confidence = 0

                    # Save doc info
                    doc_entry = {
                        "uploaded": True,
                        "filename": uploaded.name,
                        "detected_type": detected_type,
                        "confidence": confidence,
                        "raw_text": raw_text[:2000],
                        "user_confirmed": None,
                    }
                    st.session_state.docs[doc_type] = doc_entry

                    # Show classification result
                    if confidence >= 50:
                        st.success(f"✅ Detected as: **{detected_type}** ({confidence}% confidence)")
                    else:
                        st.warning(f"🤔 Detected as: **{detected_type}** (low confidence — {confidence}%)")

                    # If Annual Report — extract financial data
                    if detected_type == "Annual Report" or doc_type == "Annual Report":
                        extracted = parse_pdf(raw_bytes) if uploaded.name.endswith(".pdf") else {}
                        if extracted and not extracted.get("_error"):
                            data = {k: v_ for k, v_ in extracted.items() if not k.startswith("_")}
                            if data:
                                st.session_state.pdf_data  = data
                                st.session_state.pdf_notes = extracted.get("_raw","")
                                st.session_state.pdf_name  = uploaded.name
                                st.session_state.demo_loaded = False
                                st.info(f"📊 {len(data)} financial fields extracted!")
                                if "current_revenue" in data: st.info(f"💰 Revenue: ₹{data['current_revenue']:,.0f}")
                                if "operating_income" in data: st.info(f"📊 PAT: ₹{data['operating_income']:,.0f}")

                    st.rerun()

            elif existing.get("uploaded"):
                # Already uploaded — show status
                det = existing.get("detected_type","")
                conf = existing.get("confidence",0)
                st.success(f"✅ {existing['filename']} uploaded")
                st.caption(f"Detected: {det} ({conf}% confidence)")

                # Human-in-the-loop confirmation
                if existing.get("user_confirmed") is None:
                    st.markdown("**Is this classification correct?**")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        if st.button("✅ Correct", key=f"confirm_{doc_type}"):
                            st.session_state.docs[doc_type]["user_confirmed"] = True
                            st.rerun()
                    with c2:
                        if st.button("✏️ Change", key=f"change_{doc_type}"):
                            st.session_state.docs[doc_type]["user_confirmed"] = False
                            st.rerun()
                    with c3:
                        if st.button("🗑️ Remove", key=f"remove_{doc_type}"):
                            st.session_state.docs[doc_type] = {}
                            st.rerun()
                elif existing.get("user_confirmed") == True:
                    st.success("✅ Classification confirmed!")
                elif existing.get("user_confirmed") == False:
                    correct_type = st.selectbox(
                        "Select correct document type:",
                        list(DOC_TYPES.keys()),
                        key=f"retype_{doc_type}"
                    )
                    if st.button("✅ Save", key=f"save_{doc_type}"):
                        st.session_state.docs[doc_type]["detected_type"] = correct_type
                        st.session_state.docs[doc_type]["user_confirmed"] = True
                        st.rerun()

    # Show upload summary
    uploaded_count = sum(1 for d in st.session_state.docs.values() if d.get("uploaded"))
    if uploaded_count > 0:
        st.markdown(f'<div style="background:rgba(201,151,74,0.1);border:1px solid rgba(201,151,74,0.3);border-radius:8px;padding:8px 14px;text-align:center;"><span style="color:#c9974a;font-weight:700;">{uploaded_count}/5 documents uploaded</span></div>', unsafe_allow_html=True)

    st.markdown("---")
    analyze_btn = st.button("🚀  Run Credit Analysis", use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="main-header">
  <div class="header-badge">AI-POWERED  •  EXPLAINABLE  •  REAL-TIME</div>
  <h1>🏦 Intelli-Credit</h1>
  <p>Corporate Credit Decision Engine — Automated risk assessment aligned with bank-grade underwriting standards</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ENTITY ONBOARDING — Step 1 & 2
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.onboarding_done:
    step = st.session_state.onboarding_step

    # Progress bar
    progress = (step - 1) / 2
    st.markdown(f"""
    <div style="background:rgba(13,33,55,0.7);border:1px solid rgba(201,151,74,0.2);
        border-radius:12px;padding:20px 28px;margin-bottom:24px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
            <span style="color:#c9974a;font-weight:700;font-size:1rem;">📋 Entity Onboarding</span>
            <span style="color:rgba(255,255,255,0.4);font-size:0.82rem;">Step {step} of 2</span>
        </div>
        <div style="background:rgba(255,255,255,0.1);border-radius:10px;height:6px;">
            <div style="background:linear-gradient(90deg,#c9974a,#f59e0b);width:{int(progress*100)+50}%;height:6px;border-radius:10px;transition:width 0.3s;"></div>
        </div>
        <div style="display:flex;justify-content:space-between;margin-top:8px;">
            <span style="color:{"#c9974a" if step>=1 else "rgba(255,255,255,0.3)"};font-size:0.75rem;">🏢 Entity Details</span>
            <span style="color:{"#c9974a" if step>=2 else "rgba(255,255,255,0.3)"};font-size:0.75rem;">🏦 Loan Details</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── STEP 1: Entity Details ────────────────────────────────────────────────
    if step == 1:
        st.markdown("### 🏢 Step 1 — Entity Details")
        st.markdown('<div style="color:rgba(255,255,255,0.5);font-size:0.85rem;margin-bottom:20px;">Enter basic company information for credit assessment</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            ob_company = st.text_input("Company / Entity Name *",
                value=st.session_state.entity_data.get("company_name",""),
                placeholder="e.g. Apex Textiles Ltd.")
            ob_cin = st.text_input("CIN (Corporate Identity Number)",
                value=st.session_state.entity_data.get("cin",""),
                placeholder="e.g. U27100MH2010PTC123456")
            ob_pan = st.text_input("PAN Number",
                value=st.session_state.entity_data.get("pan",""),
                placeholder="e.g. AABCS1234C")
            ob_gstin = st.text_input("GSTIN",
                value=st.session_state.entity_data.get("gstin",""),
                placeholder="e.g. 27AABCS1234C1Z5")

        with col2:
            industry_list = list(INDUSTRY_RISK_MAP.keys())
            ob_industry = st.selectbox("Industry Sector *", industry_list,
                index=industry_list.index(st.session_state.entity_data.get("industry", industry_list[0]))
                      if st.session_state.entity_data.get("industry") in industry_list else 0)
            ob_turnover = st.number_input("Annual Turnover (₹) *",
                min_value=0.0, step=100000.0, format="%.0f",
                value=float(st.session_state.entity_data.get("turnover", 0.0)))
            ob_employees = st.selectbox("Company Size",
                ["< 10 employees","10–50 employees","50–200 employees","200–500 employees","500+ employees"],
                index=["< 10 employees","10–50 employees","50–200 employees","200–500 employees","500+ employees"].index(
                    st.session_state.entity_data.get("size","10–50 employees")))
            ob_vintage = st.number_input("Years in Business",
                min_value=0, max_value=100, step=1,
                value=int(st.session_state.entity_data.get("vintage", 0)))

        ob_address = st.text_area("Registered Address",
            value=st.session_state.entity_data.get("address",""),
            placeholder="Full registered address...", height=70)

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1,1,1])
        with c2:
            if st.button("Next — Loan Details →", use_container_width=True):
                if not ob_company:
                    st.error("❌ Company Name is required!")
                else:
                    st.session_state.entity_data = {
                        "company_name": ob_company, "cin": ob_cin,
                        "pan": ob_pan, "gstin": ob_gstin,
                        "industry": ob_industry, "turnover": ob_turnover,
                        "size": ob_employees, "vintage": ob_vintage,
                        "address": ob_address,
                    }
                    st.session_state.onboarding_step = 2
                    st.rerun()

    # ── STEP 2: Loan Details ──────────────────────────────────────────────────
    elif step == 2:
        st.markdown("### 🏦 Step 2 — Loan Details")
        st.markdown('<div style="color:rgba(255,255,255,0.5);font-size:0.85rem;margin-bottom:20px;">Specify loan requirements for credit assessment</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            loan_types = ["Term Loan","Working Capital Loan","Cash Credit (CC)","Overdraft (OD)","Letter of Credit (LC)","Bank Guarantee (BG)","Equipment Finance","Project Finance"]
            ob_loan_type = st.selectbox("Loan Type *", loan_types,
                index=loan_types.index(st.session_state.loan_data.get("loan_type","Term Loan"))
                      if st.session_state.loan_data.get("loan_type") in loan_types else 0)
            ob_loan_amt = st.number_input("Loan Amount Requested (₹) *",
                min_value=0.0, step=100000.0, format="%.0f",
                value=float(st.session_state.loan_data.get("amount", 0.0)))
            ob_tenure = st.selectbox("Loan Tenure",
                ["6 months","1 year","2 years","3 years","5 years","7 years","10 years"],
                index=["6 months","1 year","2 years","3 years","5 years","7 years","10 years"].index(
                    st.session_state.loan_data.get("tenure","3 years")))

        with col2:
            ob_purpose = st.selectbox("Loan Purpose",
                ["Business Expansion","Working Capital","Equipment Purchase","Debt Refinancing","Real Estate","Export Finance","Other"],
                index=["Business Expansion","Working Capital","Equipment Purchase","Debt Refinancing","Real Estate","Export Finance","Other"].index(
                    st.session_state.loan_data.get("purpose","Business Expansion")))
            ob_collateral = st.selectbox("Collateral Available",
                ["Immovable Property","Plant & Machinery","Stock & Receivables","No Collateral","Mixed Collateral"],
                index=["Immovable Property","Plant & Machinery","Stock & Receivables","No Collateral","Mixed Collateral"].index(
                    st.session_state.loan_data.get("collateral","Immovable Property")))
            ob_existing = st.number_input("Existing Loan Obligations (₹/year)",
                min_value=0.0, step=10000.0, format="%.0f",
                value=float(st.session_state.loan_data.get("existing_loans", 0.0)))

        ob_remarks = st.text_area("Additional Remarks",
            value=st.session_state.loan_data.get("remarks",""),
            placeholder="Any additional information for the credit team...", height=70)

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1,2,1])
        with c1:
            if st.button("← Back", use_container_width=True):
                st.session_state.onboarding_step = 1
                st.rerun()
        with c2:
            if st.button("✅ Submit & Start Credit Analysis", use_container_width=True):
                if ob_loan_amt <= 0:
                    st.error("❌ Loan Amount is required!")
                else:
                    st.session_state.loan_data = {
                        "loan_type": ob_loan_type, "amount": ob_loan_amt,
                        "tenure": ob_tenure, "purpose": ob_purpose,
                        "collateral": ob_collateral,
                        "existing_loans": ob_existing,
                        "remarks": ob_remarks,
                    }
                    st.session_state.onboarding_done = True
                    st.rerun()

    st.stop()  # Don't show rest of app until onboarding done

# ── Onboarding Summary Banner ────────────────────────────────────────────────
if st.session_state.onboarding_done and st.session_state.entity_data:
    ed = st.session_state.entity_data
    ld = st.session_state.loan_data
    if ed.get("company_name") and ed.get("company_name") != "Apex Textiles Ltd":
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(201,151,74,0.1),rgba(201,151,74,0.05));
            border:1px solid rgba(201,151,74,0.3);border-radius:10px;
            padding:12px 20px;margin-bottom:16px;display:flex;gap:24px;flex-wrap:wrap;align-items:center;">
            <span style="color:#c9974a;font-weight:700;">🏢 {ed.get('company_name','')}</span>
            <span style="color:rgba(255,255,255,0.5);font-size:0.82rem;">Industry: {ed.get('industry','')}</span>
            <span style="color:rgba(255,255,255,0.5);font-size:0.82rem;">CIN: {ed.get('cin','N/A')}</span>
            <span style="color:rgba(255,255,255,0.5);font-size:0.82rem;">PAN: {ed.get('pan','N/A')}</span>
            <span style="color:rgba(255,255,255,0.5);font-size:0.82rem;">Loan: {ld.get('loan_type','—')} | ₹{ld.get('amount',0):,.0f} | {ld.get('tenure','—')}</span>
        </div>
        """, unsafe_allow_html=True)

# Status banners
if st.session_state.pdf_data and not st.session_state.analysis_done:
    st.markdown(f"""<div style="background:linear-gradient(135deg,rgba(34,197,94,0.1),rgba(5,46,22,0.2));border:1px solid rgba(34,197,94,0.4);border-radius:10px;padding:14px 20px;margin-bottom:18px;">
    <span style="color:#22c55e;font-weight:700;">📄 PDF Loaded — {len(st.session_state.pdf_data)} fields auto-filled</span>
    <span style="color:rgba(255,255,255,0.5);font-size:0.85rem;margin-left:12px;">Review sidebar, then click Run Credit Analysis</span></div>""", unsafe_allow_html=True)

elif st.session_state.demo_loaded and not st.session_state.analysis_done:
    st.markdown("""<div style="background:linear-gradient(135deg,rgba(201,151,74,0.12),rgba(201,151,74,0.04));border:1px solid rgba(201,151,74,0.4);border-radius:10px;padding:14px 20px;margin-bottom:18px;text-align:center;">
    <span style="color:#c9974a;font-weight:700;">🎯 Demo: Apex Textiles Ltd loaded</span>
    <span style="color:rgba(255,255,255,0.5);font-size:0.85rem;margin-left:12px;">Click <b style="color:#c9974a">Run Credit Analysis</b> to see AI decision!</span></div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ANALYSIS ENGINE
# ══════════════════════════════════════════════════════════════════════════════
if analyze_btn:
    with st.spinner("🔄 Running credit analysis..."):
        # Read from session_state keys (works with key= based widgets)
        current_revenue  = float(st.session_state.get("inp_revenue",  0.0))
        previous_revenue = float(st.session_state.get("inp_prevrev",  0.0))
        ebitda           = float(st.session_state.get("inp_ebitda",   0.0))
        operating_income = float(st.session_state.get("inp_opincome", 0.0))
        interest_expense = float(st.session_state.get("inp_interest", 0.0))
        total_debt       = float(st.session_state.get("inp_debt",     0.0))
        equity           = float(st.session_state.get("inp_equity",   0.0))
        current_assets   = float(st.session_state.get("inp_cassets",  0.0))
        current_liabs    = float(st.session_state.get("inp_cliabs",   0.0))
        loan_obligation  = float(st.session_state.get("inp_loanob",   0.0))
        # Use onboarding loan amount if available, else from widget
        _ob_loan = st.session_state.loan_data.get("amount", 0.0)
        loan_amount = float(_ob_loan) if _ob_loan else float(st.session_state.get("inp_loanamt", 0.0))
        cibil_score      = float(st.session_state.get("inp_cibil",    7.0))
        promoter_stake   = int(st.session_state.get("inp_promo",      51))
        negative_news    = int(st.session_state.get("inp_negnews",    0))

        extra_notes = st.session_state.pdf_notes + " " + primary_notes

        dscr, debt_equity, revenue_growth, icr, ebitda_margin, current_ratio = calculate_ratios(
            current_revenue, previous_revenue, operating_income,
            loan_obligation, total_debt, equity,
            ebitda, interest_expense, current_assets, current_liabs
        )

        (score, category, decision, confidence, reasons, positives,
         capacity_risk, capital_risk, character_risk, conditions_risk) = calculate_risk(
            dscr, debt_equity, revenue_growth, icr, ebitda_margin, current_ratio,
            litigation_level, negative_news, promoter_stake, industry, risk_mode
        )

        note_adj, note_insights = analyze_primary_notes(extra_notes)
        score = max(0, min(100, score + note_adj))

        indian_flags = []
        if gst_compliance == "Frequent Defaults":
            score += 15; indian_flags.append("🔴 Frequent GST filing defaults — revenue inflation risk.")
        elif gst_compliance == "Minor Delays":
            score += 5;  indian_flags.append("🟡 GST filing delays — verify GSTR-2A vs 3B.")
        elif gst_compliance == "Not Registered":
            score += 20; indian_flags.append("⛔ GST not registered — regulatory non-compliance.")
        else:
            positives.append("✅ GST filings regular and compliant.")

        if cibil_score < 4:
            score += 20; indian_flags.append(f"🔴 Low CIBIL Score ({cibil_score}).")
        elif cibil_score < 6:
            score += 10; indian_flags.append(f"🟡 CIBIL {cibil_score} — below acceptable range.")
        elif cibil_score >= 8:
            positives.append(f"✅ Strong CIBIL Score ({cibil_score}).")

        if mca_status in ["Significant Gaps", "Not Filed"]:
            score += 15; indian_flags.append("🔴 MCA21/ROC non-compliance.")
        elif mca_status == "Minor Delays":
            score += 5;  indian_flags.append("🟡 MCA21 minor delays.")

        score   = max(0, min(100, score))
        reasons = note_insights + indian_flags + reasons

        if score <= 28:   category = "Low Risk";    decision = "Recommend Approval"
        elif score <= 55: category = "Medium Risk"; decision = "Approve with Conditions"
        else:             category = "High Risk";   decision = "Recommend Rejection"

        loan_rec    = recommend_loan(score, category, loan_amount, dscr, debt_equity, ebitda)
        ews_signals = get_ews_signals(dscr, revenue_growth, debt_equity, icr, current_ratio, negative_news)

        try:
            ml_result = ml_predict({
                "dscr": dscr, "debt_equity": debt_equity, "revenue_growth": revenue_growth,
                "icr": icr, "ebitda_margin": ebitda_margin, "current_ratio": current_ratio,
                "litigation_level": litigation_level, "negative_news": negative_news,
                "promoter_stake": promoter_stake, "industry": industry,
                "gst_compliance": gst_compliance, "cibil_score": cibil_score,
            })
        except Exception as e:
            ml_result = None

        st.session_state.analysis_done = True
        st.session_state.data = {
            "company_name": company_name, "industry": industry,
            "loan_amount": loan_amount, "risk_mode": risk_mode,
            "dscr": dscr, "debt_equity": debt_equity, "revenue_growth": revenue_growth,
            "icr": icr, "ebitda_margin": ebitda_margin, "current_ratio": current_ratio,
            "score": score, "category": category, "decision": decision, "confidence": confidence,
            "reasons": reasons, "positives": positives,
            "capacity_risk": capacity_risk, "capital_risk": capital_risk,
            "character_risk": character_risk, "conditions_risk": conditions_risk,
            "ews_signals": ews_signals, "loan_rec": loan_rec, "ml_result": ml_result,
            "gst_compliance": gst_compliance, "cibil_score": cibil_score, "mca_status": mca_status,
            "current_revenue": current_revenue, "previous_revenue": previous_revenue,
            "operating_income": operating_income, "loan_obligation": loan_obligation,
            "total_debt": total_debt, "equity": equity, "ebitda": ebitda,
            "interest_expense": interest_expense, "current_assets": current_assets,
            "current_liabs": current_liabs, "litigation_level": litigation_level,
            "negative_news": negative_news, "promoter_stake": promoter_stake,
        }
        try:
            save_application(st.session_state.data)
        except:
            pass


# ══════════════════════════════════════════════════════════════════════════════
# RESULTS
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.analysis_done:
    d = st.session_state.data

    if d["category"] == "Low Risk":
        css_cls = "decision-low";    icon = "🟢"; score_col = "#22c55e"
    elif d["category"] == "Medium Risk":
        css_cls = "decision-medium"; icon = "🟡"; score_col = "#f59e0b"
    else:
        css_cls = "decision-high";   icon = "🔴"; score_col = "#ef4444"

    st.markdown(f"""<div class="{css_cls}">
        <div class="decision-title" style="color:{score_col}">{icon}  {d['category'].upper()}  —  {d['decision']}</div>
        <div class="decision-sub" style="color:rgba(255,255,255,0.6)">
            {d['company_name'] or 'Company'}  |  Risk Score: <b style="color:{score_col}">{d['score']}/100</b>  |  Confidence: <b>{d['confidence']}%</b>  |  Mode: {d['risk_mode']}
        </div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    lr       = d["loan_rec"]
    lr_color = "#22c55e" if d["category"] == "Low Risk" else ("#f59e0b" if d["category"] == "Medium Risk" else "#ef4444")
    st.markdown(f"""<div style="background:linear-gradient(135deg,#0d2137,#091929);border:1px solid {lr_color}55;border-radius:10px;padding:18px 24px;margin-bottom:18px;">
        <div style="color:#c9974a;font-size:0.72rem;font-weight:600;letter-spacing:0.14em;text-transform:uppercase;margin-bottom:12px;">🏦 Loan Recommendation Engine</div>
        <div style="display:flex;gap:24px;flex-wrap:wrap;align-items:center;">
            <div style="text-align:center;min-width:140px;">
                <div style="color:rgba(255,255,255,0.4);font-size:0.68rem;text-transform:uppercase">Sanctioned Amount</div>
                <div style="color:{lr_color};font-size:1.5rem;font-weight:700;font-family:'IBM Plex Mono',monospace">{"₹ {:,.0f}".format(lr['sanctioned_amount']) if lr['sanctioned_amount'] > 0 else "—"}</div>
                <div style="color:rgba(255,255,255,0.35);font-size:0.7rem">{lr['eligibility_pct']}% of requested</div>
            </div>
            <div style="text-align:center;min-width:120px;">
                <div style="color:rgba(255,255,255,0.4);font-size:0.68rem;text-transform:uppercase">Interest Rate</div>
                <div style="color:{lr_color};font-size:1.5rem;font-weight:700;font-family:'IBM Plex Mono',monospace">{lr['interest_rate']}%</div>
                <div style="color:rgba(255,255,255,0.35);font-size:0.7rem">p.a. (MCLR + spread)</div>
            </div>
            <div style="text-align:center;min-width:100px;">
                <div style="color:rgba(255,255,255,0.4);font-size:0.68rem;text-transform:uppercase">Max Tenure</div>
                <div style="color:{lr_color};font-size:1.5rem;font-weight:700;font-family:'IBM Plex Mono',monospace">{lr['tenure_years']} Yrs</div>
            </div>
            <div style="flex:1;min-width:180px;">
                <div style="color:{lr_color};font-size:0.9rem;font-weight:600">{lr['decision_label']}</div>
                <div style="color:rgba(255,255,255,0.35);font-size:0.7rem;margin-top:4px">GST: {d['gst_compliance']}  •  CIBIL: {d['cibil_score']}  •  MCA: {d['mca_status']}</div>
            </div>
        </div></div>""", unsafe_allow_html=True)

    tab1,tab2,tab3,tab4,tab5,tab6,tab7,tab8,tab9 = st.tabs([
        "📊 Financial Ratios","📈 Risk Dashboard","⚠️ Risk Factors",
        "🔬 Stress Test","📄 CAM Report","🗄️ Portfolio",
        "🤖 ML Explainability","🔍 Research Agent","🧩 SWOT Analysis"
    ])

    # ── TAB 1: Financial Ratios ───────────────────────────────────────────────
    with tab1:
        st.markdown('<div class="section-title">Calculated Financial Ratios</div>', unsafe_allow_html=True)
        def ratio_card(label, value, benchmark, good, warn, unit="x"):
            if not value: s,c = "—","#9ca3af"
            elif value >= good: s,c = "✅ Strong","#22c55e"
            elif value >= warn: s,c = "🟡 Acceptable","#f59e0b"
            else: s,c = "🔴 Weak","#ef4444"
            return f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value" style="color:{c};font-size:1.4rem">{value:.2f}{unit}</div><div class="metric-sub">Benchmark: {benchmark} • {s}</div></div>'

        c1,c2,c3 = st.columns(3)
        with c1: st.markdown(ratio_card("DSCR",d["dscr"],"≥ 1.50x",1.5,1.2), unsafe_allow_html=True)
        with c2: st.markdown(ratio_card("ICR",d["icr"],"≥ 2.50x",2.5,1.5) if d["icr"]>0 else '<div class="metric-card"><div class="metric-label">ICR</div><div class="metric-value" style="color:#9ca3af">N/A</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(ratio_card("Debt-to-Equity",d["debt_equity"],"≤ 2.00x",0,2.0), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        c4,c5,c6 = st.columns(3)
        with c4: st.markdown(ratio_card("EBITDA Margin",d["ebitda_margin"],"≥ 15%",15,8,"%") if d["ebitda_margin"]>0 else '<div class="metric-card"><div class="metric-label">EBITDA Margin</div><div class="metric-value" style="color:#9ca3af">N/A</div></div>', unsafe_allow_html=True)
        with c5: st.markdown(ratio_card("Current Ratio",d["current_ratio"],"≥ 1.33x",1.33,1.0) if d["current_ratio"]>0 else '<div class="metric-card"><div class="metric-label">Current Ratio</div><div class="metric-value" style="color:#9ca3af">N/A</div></div>', unsafe_allow_html=True)
        with c6:
            rg = d["revenue_growth"]
            rc = "#22c55e" if rg>=10 else ("#f59e0b" if rg>=0 else "#ef4444")
            rs = "✅ Strong" if rg>=10 else ("🟡 Moderate" if rg>=0 else "🔴 Declining")
            st.markdown(f'<div class="metric-card"><div class="metric-label">Revenue Growth</div><div class="metric-value" style="color:{rc};font-size:1.4rem">{rg:.1f}%</div><div class="metric-sub">Benchmark: ≥ 10% • {rs}</div></div>', unsafe_allow_html=True)

    # ── TAB 2: Risk Dashboard ─────────────────────────────────────────────────
    with tab2:
        cg,cr = st.columns(2)
        with cg:
            st.markdown('<div class="section-title">Overall Risk Score</div>', unsafe_allow_html=True)
            gc = "#ef4444" if d["score"]>55 else ("#f59e0b" if d["score"]>28 else "#22c55e")
            fig_g = go.Figure(go.Indicator(mode="gauge+number", value=d["score"],
                number={"font":{"size":42,"color":gc,"family":"IBM Plex Mono"}},
                title={"text":f"<b>{d['category']}</b>","font":{"size":14,"color":"#c9974a"}},
                gauge={"axis":{"range":[0,100]},"bar":{"color":gc,"thickness":0.28},
                       "bgcolor":"rgba(0,0,0,0)","borderwidth":0,
                       "steps":[{"range":[0,28],"color":"rgba(34,197,94,0.15)"},
                                 {"range":[28,55],"color":"rgba(245,158,11,0.15)"},
                                 {"range":[55,100],"color":"rgba(239,68,68,0.15)"}]}))
            fig_g.update_layout(height=280,margin=dict(t=30,b=10,l=20,r=20),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_g, use_container_width=True)
        with cr:
            st.markdown('<div class="section-title">5 C\'s Risk Breakdown</div>', unsafe_allow_html=True)
            cats = ["Capacity","Capital","Character","Conditions"]
            vals = [d["capacity_risk"],d["capital_risk"],d["character_risk"],d["conditions_risk"]]
            fig_r = go.Figure(go.Scatterpolar(r=vals+[vals[0]],theta=cats+[cats[0]],
                fill="toself",fillcolor="rgba(201,151,74,0.18)",line=dict(color="#c9974a",width=2)))
            fig_r.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,100]),bgcolor="rgba(0,0,0,0)"),
                showlegend=False,height=280,margin=dict(t=20,b=20,l=20,r=20),paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_r, use_container_width=True)

        st.markdown('<div class="section-title">Weighted Score Contribution</div>', unsafe_allow_html=True)
        wts = {"Capacity (35%)":d["capacity_risk"]*0.35,"Capital (25%)":d["capital_risk"]*0.25,
               "Character (20%)":d["character_risk"]*0.20,"Conditions (20%)":d["conditions_risk"]*0.20}
        bc  = ["#ef4444" if vv>20 else ("#f59e0b" if vv>10 else "#22c55e") for vv in wts.values()]
        fig_b = go.Figure(go.Bar(x=list(wts.keys()),y=list(wts.values()),marker_color=bc,
            text=[f"{vv:.1f}" for vv in wts.values()],textposition="outside",textfont=dict(color="white",size=11)))
        fig_b.update_layout(height=260,margin=dict(t=30,b=10,l=10,r=10),paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",xaxis=dict(color="rgba(255,255,255,0.5)"),
            yaxis=dict(color="rgba(255,255,255,0.3)",gridcolor="rgba(255,255,255,0.06)"))
        st.plotly_chart(fig_b, use_container_width=True)

        st.markdown('<div class="section-title">⚡ Early Warning Signals</div>', unsafe_allow_html=True)
        for sev,msg in d["ews_signals"]:
            css = "ews-critical" if "Critical" in sev else ("ews-watch" if "Watch" in sev else "ews-clear")
            st.markdown(f'<div class="{css}"><b>{sev}</b> — {msg}</div>', unsafe_allow_html=True)

    # ── TAB 3: Risk Factors ───────────────────────────────────────────────────
    with tab3:
        c1,c2 = st.columns(2)
        with c1:
            st.markdown('<div class="section-title">⚠️ Risk Factors</div>', unsafe_allow_html=True)
            for r in (d["reasons"] or ["✅ No significant risk factors"]):
                css = "risk-pill-red" if "🔴" in r or "⛔" in r else "risk-pill-yellow"
                st.markdown(f'<div class="{css}">{r}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="section-title">✅ Positive Attributes</div>', unsafe_allow_html=True)
            for p in (d["positives"] or ["🟡 No significant positives"]):
                st.markdown(f'<div class="risk-pill-green">{p}</div>', unsafe_allow_html=True)

    # ── TAB 4: Stress Test ────────────────────────────────────────────────────
    with tab4:
        st.markdown('<div class="section-title">What-If Scenario Analysis</div>', unsafe_allow_html=True)
        s1,s2 = st.columns(2)
        with s1: rc_s = st.slider("Revenue Change (%)",-50,50,0,key="sim_rev")
        with s2: dc_s = st.slider("Debt Change (%)",-50,50,0,key="sim_dbt")
        if st.button("⚡ Run Stress Scenarios", use_container_width=True):
            scenarios = {"Base Case":(0,0),"Stress -20%":(-20,20),"Severe -40%":(-40,40),"Recovery +15%":(15,-10),"Custom":(rc_s,dc_s)}
            results = []
            for name,(rv,dv_) in scenarios.items():
                sr = d["current_revenue"]*(1+rv/100); sd = d["total_debt"]*(1+dv_/100)
                sd_,sde,sgr,sicr,sem,scr = calculate_ratios(sr,d["previous_revenue"],d["operating_income"],d["loan_obligation"],sd,d["equity"],d["ebitda"],d["interest_expense"],d["current_assets"],d["current_liabs"])
                ss,scat,_,_,_,_,_,_,_,_ = calculate_risk(sd_,sde,sgr,sicr,sem,scr,d["litigation_level"],d["negative_news"],d["promoter_stake"],d["industry"],d["risk_mode"])
                results.append({"Scenario":name,"Score":ss,"Category":scat,"DSCR":round(sd_,2),"DE":round(sde,2)})
            sc_ = ["#ef4444" if r["Score"]>55 else ("#f59e0b" if r["Score"]>28 else "#22c55e") for r in results]
            fig_s = go.Figure(go.Bar(x=[r["Scenario"] for r in results],y=[r["Score"] for r in results],
                marker_color=sc_,text=[r["Score"] for r in results],textposition="outside",textfont=dict(color="white",size=12)))
            fig_s.add_hline(y=28,line_dash="dot",line_color="#22c55e",annotation_text="Low/Medium (28)")
            fig_s.add_hline(y=55,line_dash="dot",line_color="#f59e0b",annotation_text="Medium/High (55)")
            fig_s.update_layout(height=300,margin=dict(t=40,b=10),paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",yaxis=dict(range=[0,110],color="rgba(255,255,255,0.3)",
                gridcolor="rgba(255,255,255,0.06)"),xaxis=dict(color="rgba(255,255,255,0.5)"))
            st.plotly_chart(fig_s, use_container_width=True)
            for r in results:
                cc = "#22c55e" if r["Category"]=="Low Risk" else ("#f59e0b" if r["Category"]=="Medium Risk" else "#ef4444")
                st.markdown(f'<div style="display:flex;gap:12px;padding:8px 14px;background:rgba(255,255,255,0.04);border-radius:6px;border-left:3px solid {cc};margin-bottom:5px;"><span style="color:#9ca3af;width:120px;font-size:0.82rem">{r["Scenario"]}</span><span style="color:{cc};font-weight:700;width:80px">Score: {r["Score"]}</span><span style="color:{cc};font-size:0.82rem;width:120px">{r["Category"]}</span><span style="color:rgba(255,255,255,0.5);font-size:0.78rem">DSCR: {r["DSCR"]}x | D/E: {r["DE"]}x</span></div>', unsafe_allow_html=True)

    # ── TAB 5: CAM Report ─────────────────────────────────────────────────────
    with tab5:
        st.markdown('<div class="section-title">Generate Credit Appraisal Memo</div>', unsafe_allow_html=True)
        st.markdown('<div style="background:rgba(201,151,74,0.1);border:1px solid rgba(201,151,74,0.3);border-radius:8px;padding:14px 18px;margin-bottom:16px;"><span style="color:#c9974a;font-weight:600;">📄 Bank-Grade PDF Report</span><br><span style="color:rgba(255,255,255,0.5);font-size:0.78rem;">Executive summary, ratio analysis, 5Cs scorecard, risk factors, formal recommendation.</span></div>', unsafe_allow_html=True)
        if st.button("📄 Generate CAM Report", use_container_width=True):
            with st.spinner("Generating..."):
                fn = f"CAM_{(d['company_name'] or 'Company').replace(' ','_')}.pdf"
                generate_cam(fn,d["company_name"],d["industry"],d["category"],d["decision"],d["score"],d["confidence"],d["dscr"],d["debt_equity"],d["revenue_growth"],d["icr"],d["ebitda_margin"],d["current_ratio"],d["capacity_risk"],d["capital_risk"],d["character_risk"],d["conditions_risk"],d["reasons"],d["positives"],d["risk_mode"],d["loan_amount"])
                with open(fn,"rb") as f:
                    st.download_button("⬇️  Download CAM PDF",data=f,file_name=fn,mime="application/pdf",use_container_width=True)

    # ── TAB 6: Portfolio ──────────────────────────────────────────────────────
    with tab6:
        st.markdown('<div class="section-title">Portfolio Overview</div>', unsafe_allow_html=True)
        stats = get_portfolio_stats()
        if stats["total"] == 0:
            st.info("No applications yet. Run an analysis first!")
        else:
            c1,c2,c3,c4,c5 = st.columns(5)
            c1.metric("Total",stats["total"]); c2.metric("🟢 Low",stats["low"])
            c3.metric("🟡 Medium",stats["medium"]); c4.metric("🔴 High",stats["high"])
            c5.metric("Avg Score",f"{stats['avg_score']}/100")
            cp1,cp2 = st.columns(2)
            with cp1:
                fig_pie = go.Figure(go.Pie(labels=["Low","Medium","High"],
                    values=[stats["low"],stats["medium"],stats["high"]],
                    marker_colors=["#22c55e","#f59e0b","#ef4444"],hole=0.5))
                fig_pie.update_layout(height=240,margin=dict(t=10,b=10,l=10,r=10),
                    paper_bgcolor="rgba(0,0,0,0)",legend=dict(font=dict(color="#9ca3af"),bgcolor="rgba(0,0,0,0)"))
                st.plotly_chart(fig_pie, use_container_width=True)
            with cp2:
                st.markdown(f'<div class="metric-card" style="margin-bottom:8px"><div class="metric-label">Total Requested</div><div class="metric-value" style="font-size:1.1rem">₹ {stats["total_exposure"]:,.0f}</div></div><div class="metric-card" style="margin-bottom:8px"><div class="metric-label">Total Sanctioned</div><div class="metric-value" style="font-size:1.1rem;color:#22c55e">₹ {stats["total_sanctioned"]:,.0f}</div></div><div class="metric-card"><div class="metric-label">Avg DSCR</div><div class="metric-value" style="font-size:1.1rem;color:#c9974a">{stats["avg_dscr"]}x</div></div>', unsafe_allow_html=True)
            for app in get_all_applications():
                cc = "#22c55e" if app["risk_category"]=="Low Risk" else ("#f59e0b" if app["risk_category"]=="Medium Risk" else "#ef4444")
                ca,cb = st.columns([5,1])
                with ca: st.markdown(f'<div style="background:rgba(255,255,255,0.04);border-left:3px solid {cc};border-radius:6px;padding:10px 14px;margin-bottom:5px;"><b style="color:#fff">{app["company_name"]}</b> <span style="color:#9ca3af;font-size:0.78rem">{app["industry"]} · {app["created_at"]}</span><br><span style="color:{cc};font-size:0.82rem">{app["risk_category"]}</span> <span style="color:#9ca3af;font-size:0.75rem">Score:{app["risk_score"]} · DSCR:{app["dscr"]}x · D/E:{app["debt_equity"]}x</span></div>', unsafe_allow_html=True)
                with cb:
                    if st.button("🗑️",key=f"del_{app['id']}"): delete_application(app["id"]); st.rerun()

    # ── TAB 7: ML Explainability ──────────────────────────────────────────────
    with tab7:
        ml = d.get("ml_result")
        if ml is None:
            st.warning("ML model could not run. Check scikit-learn and shap.")
        else:
            st.markdown('<div class="section-title">🤖 ML vs Rule-Based Engine</div>', unsafe_allow_html=True)
            mc  = "#22c55e" if ml["ml_category"]=="Low Risk" else ("#f59e0b" if ml["ml_category"]=="Medium Risk" else "#ef4444")
            rc2 = "#22c55e" if d["category"]=="Low Risk"     else ("#f59e0b" if d["category"]=="Medium Risk"     else "#ef4444")
            m1,m2 = st.columns(2)
            with m1: st.markdown(f'<div class="metric-card"><div class="metric-label">Rule-Based Engine</div><div class="metric-value" style="color:{rc2};font-size:1.1rem">{d["category"]}</div><div class="metric-sub">Score: {d["score"]}/100 · Confidence: {d["confidence"]}%</div></div>', unsafe_allow_html=True)
            with m2: st.markdown(f'<div class="metric-card"><div class="metric-label">ML (Random Forest)</div><div class="metric-value" style="color:{mc};font-size:1.1rem">{ml["ml_category"]}</div><div class="metric-sub">Confidence: {ml["ml_confidence"]}%</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            fig_p = go.Figure()
            for label,pct in ml["probabilities"].items():
                pc = {"Low Risk":"#22c55e","Medium Risk":"#f59e0b","High Risk":"#ef4444"}[label]
                fig_p.add_trace(go.Bar(name=label,x=[pct],y=["Probability"],orientation="h",
                    marker_color=pc,text=f"{pct}%",textposition="inside",textfont=dict(color="white",size=12)))
            fig_p.update_layout(barmode="stack",height=100,margin=dict(t=5,b=5,l=5,r=5),
                paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",showlegend=True,
                legend=dict(font=dict(color="#9ca3af"),bgcolor="rgba(0,0,0,0)",orientation="h"),
                xaxis=dict(range=[0,100]),yaxis=dict(color="rgba(255,255,255,0.3)"))
            st.plotly_chart(fig_p, use_container_width=True)

            st.markdown('<div class="section-title">🔍 SHAP — Why This Decision?</div>', unsafe_allow_html=True)
            sf=ml["shap_features"][:10]; sv=ml["shap_values"][:10]; rv=ml["raw_values"][:10]
            fl=[f'{FEATURE_LABELS.get(sf[i],sf[i])} = {rv[i]}' for i in range(len(sf))]
            bcs=["#ef4444" if vv>0 else "#22c55e" for vv in sv]
            fig_shap=go.Figure(go.Bar(x=sv,y=fl,orientation="h",marker_color=bcs,
                text=[f"+{vv:.3f}" if vv>0 else f"{vv:.3f}" for vv in sv],
                textposition="outside",textfont=dict(color="white",size=10)))
            fig_shap.add_vline(x=0,line_color="rgba(255,255,255,0.3)",line_width=1)
            fig_shap.update_layout(height=360,margin=dict(t=20,b=20,l=20,r=60),
                paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(color="rgba(255,255,255,0.4)",gridcolor="rgba(255,255,255,0.06)",
                           title="SHAP Value"),
                yaxis=dict(color="rgba(255,255,255,0.7)",tickfont=dict(size=9)))
            st.plotly_chart(fig_shap, use_container_width=True)

            fi=get_feature_importance(); fil=list(fi.keys())[:8]
            fiv=[round(vv*100,1) for vv in list(fi.values())[:8]]
            fig_fi=go.Figure(go.Bar(x=fiv,y=fil,orientation="h",marker_color="#c9974a",
                text=[f"{vv}%" for vv in fiv],textposition="outside",textfont=dict(color="white",size=10)))
            fig_fi.update_layout(height=300,margin=dict(t=10,b=10,l=20,r=60),
                paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(color="rgba(255,255,255,0.4)"),
                yaxis=dict(color="rgba(255,255,255,0.7)",tickfont=dict(size=9),autorange="reversed"))
            st.plotly_chart(fig_fi, use_container_width=True)

    # ── TAB 8: Research Agent ─────────────────────────────────────────────────
    with tab8:
        st.markdown("### 🔍 Research Agent — Digital Credit Manager")
        st.markdown("Searches company news, promoter background, legal/MCA filings, sector headwinds — adjusts risk score.")
        rc1,rc2,rc3 = st.columns([2,1,1])
        with rc1: res_company  = st.text_input("Company",value=d["company_name"],key="rc_i")
        with rc2: res_industry = st.selectbox("Industry",list(INDUSTRY_RISK_MAP.keys()),
            index=list(INDUSTRY_RISK_MAP.keys()).index(d["industry"]) if d["industry"] in INDUSTRY_RISK_MAP else 0,key="ri_i")
        with rc3: res_key = st.text_input("NewsAPI Key (Optional)",type="password",key="rk_i")

        if st.button("🔍 Run Web Research",type="primary",use_container_width=True,key="run_research"):
            with st.spinner(f"🌐 Researching {res_company}..."):
                research = run_research_agent(company_name=res_company,industry=res_industry,newsapi_key=res_key)
            rclr = {"High":"#7F1D1D","Medium":"#451A03","Low":"#052E16"}.get(research["research_risk"],"#1e293b")
            rbrd = {"High":"#EF4444","Medium":"#F59E0B","Low":"#22C55E"}.get(research["research_risk"],"#334155")
            adj  = research["score_adjustment"]; ac="#EF4444" if adj>0 else "#22C55E"; asign="+" if adj>=0 else ""
            st.markdown(f'<div style="background:{rclr};border:1px solid {rbrd};border-radius:10px;padding:18px;margin:10px 0;"><h3 style="color:white;margin:0;">{research["risk_emoji"]} Research Risk: {research["research_risk"]}</h3><p style="color:#CBD5E1;margin:8px 0 0 0;">{research["summary"]}</p><p style="color:#94A3B8;font-size:0.8em;margin:4px 0 0 0;">Score Adjustment: <b style="color:{ac};">{asign}{adj} pts</b></p></div>', unsafe_allow_html=True)
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("📰 Articles",research["total_articles"]); c2.metric("🔴 High Risk",research["high_risk_count"])
            c3.metric("🟡 Medium",research["medium_risk_count"]); c4.metric("✅ Positive",research["positive_count"])
            if research["red_flags"]:
                st.markdown("#### 🚨 Red Flags")
                for flag in research["red_flags"]: st.error(flag)
            st.markdown("---"); st.markdown("#### 📰 News")
            if research["findings"]:
                for item in research["findings"]:
                    s=item["sentiment"]; rl=item["risk_level"]
                    bc={"high":"#EF4444","medium":"#F59E0B","positive":"#22C55E","low":"#334155"}.get(rl,"#334155")
                    lh=f'<a href="{item["link"]}" target="_blank" style="color:#C9974A;font-size:0.75em;">Read →</a>' if item.get("link") else ""
                    st.markdown(f'<div style="background:#1e293b;border-left:4px solid {bc};border-radius:6px;padding:10px 14px;margin:6px 0;"><span style="color:white;font-size:0.88em;">{s["emoji"]} {item["title"]}</span> <span style="color:#94A3B8;font-size:0.72em;">{item["date"]}</span><br><span style="color:{bc};font-size:0.7em;">{rl.upper()}</span> {lh}</div>', unsafe_allow_html=True)
            else:
                st.info("No news found — clean web presence, positive signal.")
            if research.get("sector_news"):
                st.markdown(f"#### 🏭 Sector News — {res_industry}")
                for item in research["sector_news"][:5]:
                    s=item["sentiment"]
                    st.markdown(f'<div style="background:#0f172a;border:1px solid #1e293b;border-radius:6px;padding:8px 12px;margin:4px 0;"><span style="color:#CBD5E1;font-size:0.83em;">{s["emoji"]} {item["title"]}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="background:#1e293b;border:1px dashed #334155;border-radius:10px;padding:36px;text-align:center;"><h3 style="color:#64748B;">🔍 Research Not Run Yet</h3><p style="color:#475569;">Click <b style="color:#c9974a">Run Web Research</b> to auto-search:<br>📰 News  •  ⚖️ Legal  •  🏭 Sector  •  📊 Sentiment</p></div>', unsafe_allow_html=True)

    # ── TAB 9: SWOT Analysis ──────────────────────────────────────────────────
    with tab9:
        st.markdown("### 🧩 SWOT Analysis — AI Generated")
        st.markdown("Automatically generated from financial ratios, risk data, industry context, and research findings.")

        swot = generate_swot(d)

        col1, col2 = st.columns(2)

        with col1:
            # STRENGTHS
            st.markdown('''<div style="background:linear-gradient(135deg,rgba(16,85,50,0.3),rgba(5,46,22,0.5));
                border:1.5px solid rgba(34,197,94,0.5);border-radius:12px;padding:20px;margin-bottom:16px;">
                <div style="color:#22c55e;font-size:0.85rem;font-weight:700;letter-spacing:0.1em;margin-bottom:14px;">
                💪 STRENGTHS</div>''', unsafe_allow_html=True)
            for s in swot["strengths"]:
                st.markdown(f'<div style="background:rgba(34,197,94,0.08);border-left:3px solid #22c55e;border-radius:0 6px 6px 0;padding:8px 12px;margin-bottom:8px;color:rgba(255,255,255,0.85);font-size:0.82rem;">✅ {s}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # OPPORTUNITIES
            st.markdown('''<div style="background:linear-gradient(135deg,rgba(59,130,246,0.2),rgba(29,78,216,0.3));
                border:1.5px solid rgba(59,130,246,0.5);border-radius:12px;padding:20px;">
                <div style="color:#60a5fa;font-size:0.85rem;font-weight:700;letter-spacing:0.1em;margin-bottom:14px;">
                🚀 OPPORTUNITIES</div>''', unsafe_allow_html=True)
            for o in swot["opportunities"]:
                st.markdown(f'<div style="background:rgba(59,130,246,0.08);border-left:3px solid #60a5fa;border-radius:0 6px 6px 0;padding:8px 12px;margin-bottom:8px;color:rgba(255,255,255,0.85);font-size:0.82rem;">🔵 {o}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            # WEAKNESSES
            st.markdown('''<div style="background:linear-gradient(135deg,rgba(120,53,15,0.3),rgba(92,45,10,0.5));
                border:1.5px solid rgba(245,158,11,0.5);border-radius:12px;padding:20px;margin-bottom:16px;">
                <div style="color:#f59e0b;font-size:0.85rem;font-weight:700;letter-spacing:0.1em;margin-bottom:14px;">
                ⚠️ WEAKNESSES</div>''', unsafe_allow_html=True)
            for w in swot["weaknesses"]:
                st.markdown(f'<div style="background:rgba(245,158,11,0.08);border-left:3px solid #f59e0b;border-radius:0 6px 6px 0;padding:8px 12px;margin-bottom:8px;color:rgba(255,255,255,0.85);font-size:0.82rem;">⚠️ {w}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # THREATS
            st.markdown('''<div style="background:linear-gradient(135deg,rgba(127,29,29,0.3),rgba(69,10,10,0.5));
                border:1.5px solid rgba(239,68,68,0.5);border-radius:12px;padding:20px;">
                <div style="color:#ef4444;font-size:0.85rem;font-weight:700;letter-spacing:0.1em;margin-bottom:14px;">
                🔴 THREATS</div>''', unsafe_allow_html=True)
            for t in swot["threats"]:
                st.markdown(f'<div style="background:rgba(239,68,68,0.08);border-left:3px solid #ef4444;border-radius:0 6px 6px 0;padding:8px 12px;margin-bottom:8px;color:rgba(255,255,255,0.85);font-size:0.82rem;">🔴 {t}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Summary card
        st.markdown("<br>", unsafe_allow_html=True)
        score = d["score"]
        if score <= 28:
            verdict = "INVEST"; vc = "#22c55e"
        elif score <= 55:
            verdict = "CONDITIONAL INVEST"; vc = "#f59e0b"
        else:
            verdict = "DO NOT INVEST"; vc = "#ef4444"

        st.markdown(f'''<div style="background:linear-gradient(135deg,#0d2137,#091929);
            border:1px solid {vc}55;border-radius:12px;padding:20px 24px;text-align:center;">
            <div style="color:rgba(255,255,255,0.5);font-size:0.72rem;letter-spacing:0.14em;text-transform:uppercase;margin-bottom:8px;">
            SWOT INVESTMENT VERDICT</div>
            <div style="color:{vc};font-size:1.6rem;font-weight:700;">{verdict}</div>
            <div style="color:rgba(255,255,255,0.4);font-size:0.8rem;margin-top:6px;">
            Based on {len(swot["strengths"])} strengths, {len(swot["weaknesses"])} weaknesses, 
            {len(swot["opportunities"])} opportunities, {len(swot["threats"])} threats identified
            </div></div>''', unsafe_allow_html=True)

else:
    st.markdown('<div style="text-align:center;padding:60px 20px;"><div style="font-size:3.5rem;margin-bottom:16px">🏦</div><div style="color:rgba(255,255,255,0.6);font-size:1.05rem;margin-bottom:8px">Enter company details in the sidebar and click <b style="color:#c9974a">Run Credit Analysis</b></div><div style="color:rgba(255,255,255,0.3);font-size:0.82rem">6 Financial Ratios  •  5 Cs Risk Model  •  ML + SHAP  •  Research Agent  •  CAM PDF</div></div>', unsafe_allow_html=True)