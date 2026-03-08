"""
Intelli-Credit Risk Engine v2.0
Enhanced corporate credit underwriting logic
"""

INDUSTRY_RISK_MAP = {
    "IT / Technology":        {"risk": 10, "dscr_benchmark": 1.8, "de_benchmark": 1.0},
    "FMCG / Retail":          {"risk": 15, "dscr_benchmark": 1.5, "de_benchmark": 1.5},
    "Manufacturing":          {"risk": 20, "dscr_benchmark": 1.5, "de_benchmark": 2.0},
    "Pharmaceuticals":        {"risk": 20, "dscr_benchmark": 1.6, "de_benchmark": 1.5},
    "Infrastructure":         {"risk": 30, "dscr_benchmark": 1.3, "de_benchmark": 2.5},
    "Real Estate":            {"risk": 35, "dscr_benchmark": 1.2, "de_benchmark": 3.0},
    "Textiles":               {"risk": 30, "dscr_benchmark": 1.4, "de_benchmark": 2.0},
    "Financial Services":     {"risk": 25, "dscr_benchmark": 1.5, "de_benchmark": 2.0},
    "Energy / Power":         {"risk": 25, "dscr_benchmark": 1.4, "de_benchmark": 2.5},
    "Other":                  {"risk": 20, "dscr_benchmark": 1.5, "de_benchmark": 2.0},
}


def calculate_ratios(current_revenue, previous_revenue, operating_income,
                     loan_obligation, total_debt, equity,
                     ebitda, interest_expense,
                     current_assets, current_liabilities):

    # ── Revenue Growth ────────────────────────────────────────────────────
    revenue_growth = (
        ((current_revenue - previous_revenue) / previous_revenue) * 100
        if previous_revenue > 0 else 0.0
    )

    # ── DSCR ──────────────────────────────────────────────────────────────
    dscr = operating_income / loan_obligation if loan_obligation > 0 else 0.0

    # ── Debt-to-Equity ────────────────────────────────────────────────────
    debt_equity = total_debt / equity if equity > 0 else 0.0

    # ── Interest Coverage Ratio (ICR) ─────────────────────────────────────
    icr = ebitda / interest_expense if interest_expense > 0 else 0.0

    # ── EBITDA Margin ─────────────────────────────────────────────────────
    ebitda_margin = (ebitda / current_revenue) * 100 if current_revenue > 0 else 0.0

    # ── Current Ratio ─────────────────────────────────────────────────────
    current_ratio = current_assets / current_liabilities if current_liabilities > 0 else 0.0

    return dscr, debt_equity, revenue_growth, icr, ebitda_margin, current_ratio


def calculate_risk(dscr, debt_equity, revenue_growth,
                   icr, ebitda_margin, current_ratio,
                   litigation_level, negative_news,
                   promoter_stake, industry,
                   risk_mode="Balanced"):

    mode_multiplier = {"Conservative": 1.25, "Balanced": 1.0, "Aggressive": 0.80}.get(risk_mode, 1.0)
    industry_data   = INDUSTRY_RISK_MAP.get(industry, INDUSTRY_RISK_MAP["Other"])

    reasons   = []
    hard_flag = []   # Auto-reject triggers
    positives = []

    # ══════════════════════════════════════════════════════════════════════
    # CAPACITY RISK  (Weight: 35%)
    # ══════════════════════════════════════════════════════════════════════
    capacity_risk = 0

    # DSCR
    if dscr < 1.0:
        capacity_risk += 40
        hard_flag.append("⛔ DSCR < 1.0 — Company cannot cover debt obligations.")
    elif dscr < 1.25:
        capacity_risk += 25
        reasons.append("🔴 DSCR below safe threshold (1.25). Repayment risk elevated.")
    elif dscr < 1.5:
        capacity_risk += 12
        reasons.append("🟡 DSCR is moderate. Acceptable but watch for deterioration.")
    else:
        positives.append("✅ Strong DSCR indicates comfortable debt-servicing ability.")

    # ICR
    if icr > 0:
        if icr < 1.5:
            capacity_risk += 25
            reasons.append("🔴 Interest Coverage Ratio critically low — interest burden is high.")
        elif icr < 2.5:
            capacity_risk += 12
            reasons.append("🟡 Moderate Interest Coverage Ratio. Monitor interest costs.")
        elif icr < 3.5:
            capacity_risk += 5
        else:
            positives.append("✅ Healthy ICR — earnings comfortably cover interest payments.")

    # Revenue growth
    if revenue_growth < -10:
        capacity_risk += 20
        reasons.append("🔴 Revenue declining sharply (>10%). Business under severe stress.")
    elif revenue_growth < 0:
        capacity_risk += 10
        reasons.append("🟡 Revenue contraction observed.")
    elif revenue_growth > 15:
        capacity_risk -= 8
        positives.append("✅ Strong revenue growth trend noted.")

    # EBITDA Margin
    if ebitda_margin > 0:
        if ebitda_margin < 5:
            capacity_risk += 15
            reasons.append("🔴 Very thin EBITDA margin — limited buffer against cost shocks.")
        elif ebitda_margin < 10:
            capacity_risk += 8
            reasons.append("🟡 Below-average EBITDA margin for most industries.")
        elif ebitda_margin > 20:
            capacity_risk -= 5
            positives.append("✅ Strong EBITDA margin reflects operational efficiency.")

    capacity_risk = max(0, capacity_risk)

    # ══════════════════════════════════════════════════════════════════════
    # CAPITAL RISK  (Weight: 25%)
    # ══════════════════════════════════════════════════════════════════════
    capital_risk = 0
    de_benchmark = industry_data["de_benchmark"]

    if debt_equity > de_benchmark * 1.5:
        capital_risk += 30
        reasons.append(f"🔴 Leverage extremely high (D/E {debt_equity:.1f}x vs industry ~{de_benchmark}x).")
    elif debt_equity > de_benchmark:
        capital_risk += 18
        reasons.append(f"🟡 Debt-to-Equity exceeds industry benchmark of {de_benchmark}x.")
    elif debt_equity > de_benchmark * 0.5:
        capital_risk += 8
    else:
        positives.append("✅ Conservative leverage — strong balance sheet.")

    # Current Ratio (liquidity)
    if current_ratio > 0:
        if current_ratio < 1.0:
            capital_risk += 20
            hard_flag.append("⛔ Current Ratio < 1.0 — Immediate liquidity risk.")
        elif current_ratio < 1.33:
            capital_risk += 10
            reasons.append("🟡 Current ratio below RBI's recommended 1.33 for working capital loans.")
        else:
            positives.append("✅ Adequate liquidity — Current Ratio above benchmark.")

    capital_risk = max(0, capital_risk)

    # ══════════════════════════════════════════════════════════════════════
    # CHARACTER RISK  (Weight: 20%)
    # ══════════════════════════════════════════════════════════════════════
    character_risk = 0

    if litigation_level == "High":
        character_risk += 30
        hard_flag.append("⛔ Severe litigation exposure — requires legal clearance.")
    elif litigation_level == "Medium":
        character_risk += 15
        reasons.append("🟡 Pending litigation — legal outcome uncertain.")
    else:
        positives.append("✅ Clean litigation record.")

    if negative_news > 5:
        character_risk += 20
        reasons.append("🔴 High negative media coverage detected.")
    elif negative_news > 2:
        character_risk += 10
        reasons.append("🟡 Moderate adverse media exposure.")

    # Promoter stake
    if promoter_stake < 26:
        character_risk += 20
        reasons.append("🔴 Very low promoter stake — limited 'skin in the game'.")
    elif promoter_stake < 40:
        character_risk += 10
        reasons.append("🟡 Promoter stake below recommended 40%.")
    elif promoter_stake >= 51:
        character_risk -= 10
        positives.append(f"✅ Strong promoter commitment ({promoter_stake}% stake).")

    character_risk = max(0, character_risk)

    # ══════════════════════════════════════════════════════════════════════
    # CONDITIONS RISK  (Industry / Macro) — Weight: 20%
    # ══════════════════════════════════════════════════════════════════════
    conditions_risk = industry_data["risk"]
    if conditions_risk >= 30:
        reasons.append(f"🟡 {industry} sector carries elevated macro/regulatory risk.")
    elif conditions_risk <= 15:
        positives.append(f"✅ {industry} is a relatively stable sector.")

    # ══════════════════════════════════════════════════════════════════════
    # WEIGHTED TOTAL SCORE  (scale 0–100)
    # ══════════════════════════════════════════════════════════════════════
    raw_score = (
        (capacity_risk   * 0.35) +
        (capital_risk    * 0.25) +
        (character_risk  * 0.20) +
        (conditions_risk * 0.20)
    )

    # Hard-limit penalty
    hard_penalty = len(hard_flag) * 15

    risk_score = min(100, int((raw_score + hard_penalty) * mode_multiplier))

    # ── Classification ────────────────────────────────────────────────────
    if hard_flag:
        category = "High Risk"
        decision = "Recommend Rejection"
    elif risk_score <= 28:
        category = "Low Risk"
        decision = "Recommend Approval"
    elif risk_score <= 55:
        category = "Medium Risk"
        decision = "Approve with Conditions"
    else:
        category = "High Risk"
        decision = "Recommend Rejection"

    # ── Confidence ────────────────────────────────────────────────────────
    # Higher confidence the further score is from the boundary
    if risk_score <= 28:
        confidence = min(95, 70 + (28 - risk_score))
    elif risk_score <= 55:
        confidence = 60
    else:
        confidence = min(95, 60 + (risk_score - 55))

    all_reasons = hard_flag + reasons

    return (risk_score, category, decision, int(confidence),
            all_reasons, positives,
            int(capacity_risk), int(capital_risk),
            int(character_risk), int(conditions_risk))


def analyze_primary_notes(notes: str):
    """Enhanced keyword engine for primary due-diligence notes."""
    text = notes.lower()
    adj  = 0
    insights = []

    # Negative signals
    red_flags = {
        "fraud":              (40, "⛔ Fraud concern identified in credit officer notes."),
        "money laundering":   (40, "⛔ Money laundering reference flagged in notes."),
        "default":            (25, "🔴 Prior default history mentioned by credit officer."),
        "penalty":            (20, "🔴 Regulatory penalty risk noted."),
        "npa":                (25, "🔴 NPA classification risk mentioned."),
        "going concern":      (30, "⛔ Going-concern qualification noted — serious red flag."),
        "loss":               (15, "🟡 Net loss reported in officer notes."),
        "low capacity":       (15, "🟡 Below-capacity utilisation flagged."),
        "40% capacity":       (15, "🟡 Only 40% operational capacity utilisation noted."),
        "dispute":            (12, "🟡 Dispute mentioned in officer notes."),
        "delay":              (10, "🟡 Payment/delivery delays noted."),
    }

    # Positive signals
    green_flags = {
        "strong management":   (-15, "✅ Strong management quality noted by officer."),
        "experienced team":    (-12, "✅ Experienced management team acknowledged."),
        "growing demand":      (-10, "✅ Positive demand outlook noted."),
        "export revenue":      (-10, "✅ Export diversification — positive forex earner."),
        "debt free":           (-20, "✅ Company is effectively debt-free per officer notes."),
        "market leader":       (-12, "✅ Market leadership position acknowledged."),
        "iso certified":       ( -8, "✅ ISO certification noted — process quality indicator."),
        "consistent dividend": (-10, "✅ Consistent dividend history — strong governance signal."),
    }

    for kw, (score, msg) in red_flags.items():
        if kw in text:
            adj += score
            insights.append(msg)

    for kw, (score, msg) in green_flags.items():
        if kw in text:
            adj += score
            insights.append(msg)

    return adj, insights


def get_industry_benchmarks(industry: str) -> dict:
    return INDUSTRY_RISK_MAP.get(industry, INDUSTRY_RISK_MAP["Other"])


def recommend_loan(score: int, category: str, requested_amount: float,
                   dscr: float, debt_equity: float, ebitda: float) -> dict:
    """
    Suggest sanctioned loan amount and risk-adjusted interest rate.
    Logic mirrors how Indian banks / NBFCs price credit.
    """
    base_rate = 9.5  # Base lending rate (approx MCLR + spread)

    if category == "Low Risk":
        eligibility_pct  = 0.90
        spread           = 0.50
        tenure_years     = 7
        decision_label   = "Recommend Full / Near-Full Sanction"
    elif category == "Medium Risk":
        eligibility_pct  = 0.65
        spread           = 1.75
        tenure_years     = 5
        decision_label   = "Conditional Sanction — Reduced Limit"
    else:
        eligibility_pct  = 0.0
        spread           = 4.00
        tenure_years     = 0
        decision_label   = "Decline — Restructure & Reapply"

    interest_rate      = round(base_rate + spread, 2)
    sanctioned_amount  = requested_amount * eligibility_pct

    # DSCR-based cap: max loan = EBITDA × tenure × 0.8
    if ebitda > 0 and tenure_years > 0:
        dscr_cap = ebitda * tenure_years * 0.8
        sanctioned_amount = min(sanctioned_amount, dscr_cap)

    return {
        "sanctioned_amount": round(sanctioned_amount),
        "interest_rate":     interest_rate,
        "tenure_years":      tenure_years,
        "decision_label":    decision_label,
        "eligibility_pct":   int(eligibility_pct * 100),
    }


def get_ews_signals(dscr, revenue_growth, debt_equity, icr, current_ratio, negative_news) -> list:
    """Early Warning Signal generator — bank-style monitoring flags."""
    signals = []

    if dscr < 1.2:
        signals.append(("🔴 Critical", "DSCR approaching breach level (<1.2)"))
    elif dscr < 1.5:
        signals.append(("🟡 Watch", "DSCR in watch zone — monitor quarterly"))

    if revenue_growth < -5:
        signals.append(("🔴 Critical", "Revenue contraction exceeding 5%"))

    if debt_equity > 3.0:
        signals.append(("🔴 Critical", "Leverage beyond 3x — escalate to credit committee"))

    if icr > 0 and icr < 2.0:
        signals.append(("🟡 Watch", "ICR falling — interest servicing under pressure"))

    if current_ratio > 0 and current_ratio < 1.2:
        signals.append(("🟡 Watch", "Liquidity tightening — current ratio below 1.2"))

    if negative_news > 3:
        signals.append(("🟡 Watch", "Rising negative media sentiment — reputational risk"))

    if not signals:
        signals.append(("🟢 Clear", "No early warning signals detected"))

    return signals