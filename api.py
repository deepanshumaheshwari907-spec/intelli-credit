"""
Intelli-Credit FastAPI Backend v1.0
Production-grade REST API for corporate credit decisioning
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import sys
import os

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from risk_engine import (
    calculate_ratios, calculate_risk, analyze_primary_notes,
    get_ews_signals, recommend_loan, INDUSTRY_RISK_MAP
)
from database import (
    save_application, get_all_applications,
    get_portfolio_stats, delete_application
)

try:
    from ml_engine import ml_predict, get_feature_importance, FEATURE_LABELS
    ML_AVAILABLE = True
except Exception:
    ML_AVAILABLE = False

# ── App Init ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="Intelli-Credit API",
    description="""
## 🏦 AI-Powered Corporate Credit Decision Engine

REST API for automated corporate loan appraisal.

### Features
- **6-ratio financial analysis** (DSCR, ICR, D/E, EBITDA, Current Ratio, Revenue Growth)
- **Explainable 5 Cs scoring** with weighted components
- **Indian context** — GST, CIBIL, MCA21 risk adjustments
- **ML model** — Random Forest + SHAP explainability
- **Loan recommendation** — sanctioned amount + interest rate
- **Early Warning Signals** — 6-parameter EWS system
- **Portfolio history** — SQLite persistence
    """,
    version="2.0.0",
    contact={"name": "Intelli-Credit Team", "email": "deepanshu@intellicredit.ai"},
)

# ── CORS — allow Streamlit frontend ───────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ══════════════════════════════════════════════════════════════════════════
# REQUEST / RESPONSE MODELS
# ══════════════════════════════════════════════════════════════════════════

class CreditRequest(BaseModel):
    # Company
    company_name:     str            = Field(..., example="Apex Textiles Ltd")
    industry:         str            = Field("Other", example="Textiles")
    loan_amount:      float          = Field(0, example=5000000)
    risk_mode:        str            = Field("Balanced", example="Balanced")

    # P&L
    current_revenue:  float          = Field(..., example=50000000)
    previous_revenue: float          = Field(..., example=42000000)
    ebitda:           float          = Field(0, example=8000000)
    operating_income: float          = Field(..., example=6500000)
    interest_expense: float          = Field(0, example=2000000)

    # Balance Sheet
    total_debt:       float          = Field(..., example=25000000)
    equity:           float          = Field(..., example=12000000)
    current_assets:   float          = Field(0, example=18000000)
    current_liabs:    float          = Field(0, example=14000000)
    loan_obligation:  float          = Field(..., example=4000000)

    # Qualitative
    promoter_stake:   float          = Field(51, example=45)
    litigation_level: str            = Field("Low", example="Medium")
    negative_news:    int            = Field(0, example=3)
    primary_notes:    Optional[str]  = Field("", example="Strong management team noted.")

    # Indian Context
    gst_compliance:   str            = Field("Regular & Compliant")
    cibil_score:      float          = Field(7.0, example=7.5)
    mca_status:       str            = Field("Up to Date")


class RatioResponse(BaseModel):
    dscr:           float
    debt_equity:    float
    revenue_growth: float
    icr:            float
    ebitda_margin:  float
    current_ratio:  float


class LoanRecommendation(BaseModel):
    sanctioned_amount: float
    interest_rate:     float
    tenure_years:      int
    decision_label:    str
    eligibility_pct:   int


class CreditResponse(BaseModel):
    company_name:    str
    industry:        str
    ratios:          RatioResponse
    risk_score:      int
    risk_category:   str
    decision:        str
    confidence:      int
    capacity_risk:   int
    capital_risk:    int
    character_risk:  int
    conditions_risk: int
    loan_rec:        LoanRecommendation
    risk_factors:    list
    positives:       list
    ews_signals:     list
    ml_available:    bool
    ml_category:     Optional[str]  = None
    ml_confidence:   Optional[float]= None
    probabilities:   Optional[dict] = None
    saved_id:        Optional[int]  = None


# ══════════════════════════════════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════════════════════════════════

@app.get("/", tags=["Health"])
def root():
    return {
        "service":     "Intelli-Credit API",
        "version":     "2.0.0",
        "status":      "running",
        "ml_enabled":  ML_AVAILABLE,
        "docs":        "/docs",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy", "ml_available": ML_AVAILABLE}


@app.get("/industries", tags=["Reference"])
def get_industries():
    """List all supported industries with benchmarks."""
    return {"industries": list(INDUSTRY_RISK_MAP.keys())}


# ── MAIN CREDIT ANALYSIS ──────────────────────────────────────────────────
@app.post("/analyze", response_model=CreditResponse, tags=["Credit Analysis"])
def analyze_credit(req: CreditRequest):
    """
    **Core endpoint** — Full credit analysis pipeline.

    Accepts company financials + qualitative inputs.
    Returns risk score, category, loan recommendation, SHAP explanations.
    """
    try:
        # Step 1: Calculate ratios
        dscr, de, rev_g, icr, ebitda_m, cr = calculate_ratios(
            req.current_revenue, req.previous_revenue,
            req.operating_income, req.loan_obligation,
            req.total_debt, req.equity,
            req.ebitda, req.interest_expense,
            req.current_assets, req.current_liabs
        )

        # Step 2: Risk scoring
        (score, category, decision, confidence,
         reasons, positives,
         cap_risk, cap_ital, char_risk, cond_risk) = calculate_risk(
            dscr, de, rev_g, icr, ebitda_m, cr,
            req.litigation_level, req.negative_news,
            req.promoter_stake, req.industry, req.risk_mode
        )

        # Step 3: Notes NLP
        note_adj, note_insights = analyze_primary_notes(req.primary_notes or "")
        score   = max(0, min(100, score + note_adj))
        reasons = note_insights + reasons

        # Step 4: Indian context
        if req.gst_compliance == "Frequent Defaults":
            score += 15; reasons.append("🔴 GST frequent defaults detected.")
        elif req.gst_compliance == "Minor Delays":
            score += 5
        elif req.gst_compliance == "Not Registered":
            score += 20; reasons.append("⛔ GST not registered.")

        if req.cibil_score < 4:
            score += 20; reasons.append(f"🔴 Low CIBIL score ({req.cibil_score})")
        elif req.cibil_score < 6:
            score += 10

        if req.mca_status in ["Significant Gaps", "Not Filed"]:
            score += 15; reasons.append("🔴 MCA21 non-compliance.")

        score = max(0, min(100, score))

        # Recategorize
        if score <= 28:
            category = "Low Risk";    decision = "Recommend Approval"
        elif score <= 55:
            category = "Medium Risk"; decision = "Approve with Conditions"
        else:
            category = "High Risk";   decision = "Recommend Rejection"

        # Step 5: Loan recommendation
        loan_rec = recommend_loan(score, category, req.loan_amount, dscr, de, req.ebitda)

        # Step 6: EWS
        ews = get_ews_signals(dscr, rev_g, de, icr, cr, req.negative_news)

        # Step 7: ML (optional)
        ml_category = ml_conf = proba = None
        if ML_AVAILABLE:
            try:
                ml_res      = ml_predict({
                    "dscr": dscr, "debt_equity": de, "revenue_growth": rev_g,
                    "icr": icr, "ebitda_margin": ebitda_m, "current_ratio": cr,
                    "litigation_level": req.litigation_level,
                    "negative_news": req.negative_news,
                    "promoter_stake": req.promoter_stake,
                    "industry": req.industry,
                    "gst_compliance": req.gst_compliance,
                    "cibil_score": req.cibil_score,
                })
                ml_category = ml_res["ml_category"]
                ml_conf     = ml_res["ml_confidence"]
                proba       = ml_res["probabilities"]
            except Exception:
                pass

        # Step 8: Save to DB
        session_data = {
            "company_name": req.company_name, "industry": req.industry,
            "loan_amount": req.loan_amount,   "risk_mode": req.risk_mode,
            "dscr": dscr, "debt_equity": de,  "revenue_growth": rev_g,
            "icr": icr, "ebitda_margin": ebitda_m, "current_ratio": cr,
            "score": score, "category": category, "decision": decision,
            "confidence": confidence, "reasons": reasons, "positives": positives,
            "capacity_risk": cap_risk, "capital_risk": cap_ital,
            "character_risk": char_risk, "conditions_risk": cond_risk,
            "loan_rec": loan_rec, "gst_compliance": req.gst_compliance,
            "cibil_score": req.cibil_score, "mca_status": req.mca_status,
        }
        saved_id = save_application(session_data)

        return CreditResponse(
            company_name=req.company_name, industry=req.industry,
            ratios=RatioResponse(
                dscr=round(dscr,3), debt_equity=round(de,3),
                revenue_growth=round(rev_g,2), icr=round(icr,3),
                ebitda_margin=round(ebitda_m,2), current_ratio=round(cr,3)
            ),
            risk_score=score, risk_category=category,
            decision=decision, confidence=confidence,
            capacity_risk=cap_risk, capital_risk=cap_ital,
            character_risk=char_risk, conditions_risk=cond_risk,
            loan_rec=LoanRecommendation(**loan_rec),
            risk_factors=reasons, positives=positives,
            ews_signals=[f"{s} — {m}" for s, m in ews],
            ml_available=ML_AVAILABLE,
            ml_category=ml_category, ml_confidence=ml_conf,
            probabilities=proba, saved_id=saved_id,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── PORTFOLIO ─────────────────────────────────────────────────────────────
@app.get("/portfolio", tags=["Portfolio"])
def get_portfolio():
    """Get all saved applications + portfolio stats."""
    return {
        "stats":        get_portfolio_stats(),
        "applications": get_all_applications(),
    }


@app.get("/portfolio/stats", tags=["Portfolio"])
def portfolio_stats():
    """Aggregate portfolio statistics."""
    return get_portfolio_stats()


@app.delete("/portfolio/{app_id}", tags=["Portfolio"])
def remove_application(app_id: int):
    """Delete a saved application by ID."""
    delete_application(app_id)
    return {"deleted": True, "id": app_id}


# ── ML ────────────────────────────────────────────────────────────────────
@app.get("/ml/feature-importance", tags=["ML"])
def feature_importance():
    """Global feature importance from trained Random Forest model."""
    if not ML_AVAILABLE:
        raise HTTPException(status_code=503, detail="ML engine not available")
    return {"feature_importance": get_feature_importance()}


@app.get("/ml/status", tags=["ML"])
def ml_status():
    return {
        "ml_available": ML_AVAILABLE,
        "model": "Random Forest (200 estimators)",
        "features": 12,
        "classes": ["Low Risk", "Medium Risk", "High Risk"],
        "explainability": "SHAP TreeExplainer",
    }


# ── Run directly ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)