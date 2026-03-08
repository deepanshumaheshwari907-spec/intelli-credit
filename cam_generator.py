"""
Intelli-Credit CAM Generator v2.0
Professional Credit Appraisal Memo — bank-grade PDF output
"""

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, ListFlowable, ListItem, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime

# ── Brand Colours ──────────────────────────────────────────────────────────
NAVY        = colors.HexColor("#0d2137")
GOLD        = colors.HexColor("#c9974a")
LIGHT_BLUE  = colors.HexColor("#e8f0f7")
WHITE       = colors.white
GREEN       = colors.HexColor("#1a7a4a")
AMBER       = colors.HexColor("#b45309")
RED_DARK    = colors.HexColor("#9b1c1c")
GREY_LIGHT  = colors.HexColor("#f5f5f5")
GREY_MID    = colors.HexColor("#9ca3af")
TEXT_DARK   = colors.HexColor("#1f2937")


def _styles():
    base = getSampleStyleSheet()

    custom = {
        "BankTitle": ParagraphStyle(
            "BankTitle", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=22,
            textColor=WHITE, alignment=TA_CENTER, spaceAfter=4
        ),
        "BankSubtitle": ParagraphStyle(
            "BankSubtitle", parent=base["Normal"],
            fontName="Helvetica", fontSize=11,
            textColor=GOLD, alignment=TA_CENTER, spaceAfter=2
        ),
        "SectionHead": ParagraphStyle(
            "SectionHead", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=12,
            textColor=NAVY, spaceBefore=14, spaceAfter=6,
            borderPad=4, leading=16
        ),
        "Body": ParagraphStyle(
            "Body", parent=base["Normal"],
            fontName="Helvetica", fontSize=9.5,
            textColor=TEXT_DARK, leading=14, spaceAfter=4
        ),
        "BoldBody": ParagraphStyle(
            "BoldBody", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=9.5,
            textColor=TEXT_DARK, leading=14
        ),
        "RiskGreen": ParagraphStyle(
            "RiskGreen", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=14,
            textColor=GREEN, alignment=TA_CENTER
        ),
        "RiskAmber": ParagraphStyle(
            "RiskAmber", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=14,
            textColor=AMBER, alignment=TA_CENTER
        ),
        "RiskRed": ParagraphStyle(
            "RiskRed", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=14,
            textColor=RED_DARK, alignment=TA_CENTER
        ),
        "SmallGrey": ParagraphStyle(
            "SmallGrey", parent=base["Normal"],
            fontName="Helvetica", fontSize=8,
            textColor=GREY_MID, alignment=TA_CENTER
        ),
        "Footer": ParagraphStyle(
            "Footer", parent=base["Normal"],
            fontName="Helvetica-Oblique", fontSize=7.5,
            textColor=GREY_MID, alignment=TA_CENTER
        ),
    }
    return custom


def _section(title, styles):
    elems = []
    elems.append(Spacer(1, 0.08 * inch))
    elems.append(HRFlowable(width="100%", thickness=1.5, color=NAVY, spaceAfter=4))
    elems.append(Paragraph(title.upper(), styles["SectionHead"]))
    return elems


def generate_cam(filename, company_name, industry, category, decision,
                 score, confidence, dscr, debt_equity, revenue_growth,
                 icr, ebitda_margin, current_ratio,
                 capacity_risk, capital_risk, character_risk, conditions_risk,
                 reasons, positives, risk_mode, loan_amount=0):

    doc = SimpleDocTemplate(
        filename, pagesize=A4,
        leftMargin=0.65 * inch, rightMargin=0.65 * inch,
        topMargin=0.5 * inch, bottomMargin=0.65 * inch
    )
    styles = _styles()
    elems  = []
    date_str = datetime.now().strftime("%d %B %Y  |  %H:%M hrs")

    # ── HEADER BANNER ─────────────────────────────────────────────────────
    header_data = [[
        Paragraph("INTELLI-CREDIT", styles["BankTitle"]),
    ]]
    header_tbl = Table(header_data, colWidths=[6.7 * inch])
    header_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), NAVY),
        ("TOPPADDING",   (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
        ("ROUNDEDCORNERS", [6]),
    ]))
    elems.append(header_tbl)

    sub_data = [[Paragraph("AI-Powered Corporate Credit Decision Engine  |  Credit Appraisal Memorandum", styles["BankSubtitle"])]]
    sub_tbl = Table(sub_data, colWidths=[6.7 * inch])
    sub_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#0a1929")),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    elems.append(sub_tbl)
    elems.append(Spacer(1, 0.15 * inch))

    # ── DATE / REF ─────────────────────────────────────────────────────────
    ref_num = f"CAM-{datetime.now().strftime('%Y%m%d%H%M')}"
    elems.append(Paragraph(f"Report Date: {date_str}   |   Ref: {ref_num}", styles["SmallGrey"]))
    elems.append(Spacer(1, 0.12 * inch))

    # ── COMPANY PROFILE ───────────────────────────────────────────────────
    elems += _section("1. Company Profile", styles)
    profile_data = [
        ["Company Name",    company_name or "—",          "Industry Sector", industry],
        ["Loan Amount Req.", f"₹ {loan_amount:,.0f}" if loan_amount else "—", "Assessment Mode", risk_mode],
    ]
    p_tbl = Table(profile_data, colWidths=[1.6*inch, 2.0*inch, 1.6*inch, 1.5*inch])
    p_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, -1), LIGHT_BLUE),
        ("BACKGROUND",    (2, 0), (2, -1), LIGHT_BLUE),
        ("FONTNAME",      (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",      (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
    ]))
    elems.append(p_tbl)

    # ── CREDIT DECISION BOX ───────────────────────────────────────────────
    elems += _section("2. Credit Decision Summary", styles)

    if category == "Low Risk":
        bg_col   = colors.HexColor("#d1fae5")
        border   = GREEN
        r_style  = styles["RiskGreen"]
        dec_icon = "✅"
    elif category == "Medium Risk":
        bg_col   = colors.HexColor("#fef3c7")
        border   = AMBER
        r_style  = styles["RiskAmber"]
        dec_icon = "⚠️"
    else:
        bg_col   = colors.HexColor("#fee2e2")
        border   = RED_DARK
        r_style  = styles["RiskRed"]
        dec_icon = "❌"

    decision_data = [
        [
            Paragraph(f"{dec_icon} {category}", r_style),
            Paragraph(decision, r_style),
            Paragraph(f"Score: {score}/100", r_style),
            Paragraph(f"Confidence: {confidence}%", r_style),
        ]
    ]
    d_tbl = Table(decision_data, colWidths=[1.6*inch, 2.0*inch, 1.6*inch, 1.5*inch])
    d_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), bg_col),
        ("BOX",           (0, 0), (-1, -1), 2, border),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
    ]))
    elems.append(d_tbl)

    # ── FINANCIAL RATIOS ──────────────────────────────────────────────────
    elems += _section("3. Financial Ratio Analysis", styles)

    def _bench(val, good, warn):
        if val >= good:   return "✅ Strong"
        if val >= warn:   return "🟡 Acceptable"
        return "🔴 Weak"

    ratio_rows = [
        ["Metric", "Value", "Benchmark", "Assessment"],
        ["DSCR (Debt Service Coverage)",
         f"{dscr:.2f}x",       "≥ 1.50x",  _bench(dscr, 1.5, 1.2)],
        ["Interest Coverage Ratio (ICR)",
         f"{icr:.2f}x" if icr else "N/A",   "≥ 2.50x",  _bench(icr, 2.5, 1.5) if icr else "—"],
        ["Debt-to-Equity Ratio",
         f"{debt_equity:.2f}x", "≤ 2.00x",
         "✅ Strong" if debt_equity <= 1.5 else ("🟡 Acceptable" if debt_equity <= 2.5 else "🔴 Weak")],
        ["EBITDA Margin",
         f"{ebitda_margin:.1f}%" if ebitda_margin else "N/A", "≥ 15%",
         _bench(ebitda_margin, 15, 8) if ebitda_margin else "—"],
        ["Current Ratio",
         f"{current_ratio:.2f}x" if current_ratio else "N/A", "≥ 1.33x",
         _bench(current_ratio, 1.33, 1.0) if current_ratio else "—"],
        ["Revenue Growth",
         f"{revenue_growth:.1f}%", "≥ 10%",
         "✅ Strong" if revenue_growth >= 10 else ("🟡 Acceptable" if revenue_growth >= 0 else "🔴 Declining")],
    ]

    r_tbl = Table(ratio_rows, colWidths=[2.5*inch, 1.1*inch, 1.2*inch, 1.9*inch])
    r_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, GREY_LIGHT]),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
    ]))
    elems.append(r_tbl)

    # ── RISK BREAKDOWN ────────────────────────────────────────────────────
    elems += _section("4. Risk Component Breakdown (Weighted Scorecard)", styles)

    breakdown = [
        ["Risk Dimension",    "Score", "Weight", "Contribution"],
        ["Capacity Risk",     str(capacity_risk),   "35%", f"{int(capacity_risk*0.35)}"],
        ["Capital Risk",      str(capital_risk),    "25%", f"{int(capital_risk*0.25)}"],
        ["Character Risk",    str(character_risk),  "20%", f"{int(character_risk*0.20)}"],
        ["Conditions Risk",   str(conditions_risk), "20%", f"{int(conditions_risk*0.20)}"],
        ["TOTAL RISK SCORE",  "",                   "100%", str(score)],
    ]
    b_tbl = Table(breakdown, colWidths=[2.5*inch, 1.0*inch, 1.1*inch, 2.1*inch])
    b_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND",    (0, -1),(-1, -1), colors.HexColor("#1e3a5f")),
        ("TEXTCOLOR",     (0, -1),(-1, -1), WHITE),
        ("FONTNAME",      (0, -1),(-1, -1), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS",(0, 1), (-1, -2), [WHITE, GREY_LIGHT]),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("ALIGN",         (1, 0), (-1, -1), "CENTER"),
    ]))
    elems.append(b_tbl)

    # ── RISK FACTORS ──────────────────────────────────────────────────────
    if reasons:
        elems += _section("5. Key Risk Factors Identified", styles)
        risk_items = [ListItem(Paragraph(r, styles["Body"]), leftIndent=12) for r in reasons]
        elems.append(ListFlowable(risk_items, bulletType="bullet", bulletColor=RED_DARK, leftIndent=0))

    if positives:
        elems += _section("6. Positive Credit Attributes", styles)
        pos_items = [ListItem(Paragraph(p, styles["Body"]), leftIndent=12) for p in positives]
        elems.append(ListFlowable(pos_items, bulletType="bullet", bulletColor=GREEN, leftIndent=0))

    # ── ANALYST NARRATIVE ─────────────────────────────────────────────────
    elems += _section("7. Analyst Narrative & Recommendation", styles)

    if category == "Low Risk":
        narrative = (
            f"<b>{company_name or 'The applicant'}</b> demonstrates a strong financial profile with "
            f"a DSCR of {dscr:.2f}x, indicating robust debt-service capability. The leverage "
            f"position is within acceptable limits, and qualitative risk indicators are benign. "
            f"The credit committee may consider approving the facility subject to standard covenants "
            f"including quarterly financial reporting and maintenance of DSCR ≥ 1.25x."
        )
    elif category == "Medium Risk":
        narrative = (
            f"<b>{company_name or 'The applicant'}</b> presents a mixed credit profile. While certain "
            f"financial metrics are adequate, areas of concern — including leverage at {debt_equity:.2f}x "
            f"and DSCR of {dscr:.2f}x — warrant enhanced monitoring. Approval may be considered "
            f"with stringent financial covenants, additional collateral, and a structured drawdown "
            f"linked to milestone compliance. A review within 6 months is recommended."
        )
    else:
        narrative = (
            f"<b>{company_name or 'The applicant'}</b> presents significant credit risks that preclude "
            f"sanction under current parameters. Key concerns include elevated leverage, weakening "
            f"debt-service coverage, and/or adverse qualitative indicators. The credit officer "
            f"recommends declining the current application. The applicant may reapply upon demonstrating "
            f"material improvement in financial metrics over two consecutive quarters."
        )

    elems.append(Paragraph(narrative, styles["Body"]))

    # ── DISCLAIMER ────────────────────────────────────────────────────────
    elems.append(Spacer(1, 0.3 * inch))
    elems.append(HRFlowable(width="100%", thickness=0.5, color=GREY_MID))
    elems.append(Spacer(1, 0.08 * inch))
    disclaimer = (
        "CONFIDENTIAL — This Credit Appraisal Memo is generated by the Intelli-Credit AI Engine "
        "for evaluation and research purposes only. It does not constitute a binding credit decision "
        "or financial advice. All credit decisions remain subject to the lending institution's "
        "internal policies, regulatory guidelines, and final approval by the credit committee."
    )
    elems.append(Paragraph(disclaimer, styles["Footer"]))
    elems.append(Paragraph(f"Generated by Intelli-Credit AI Engine  •  {date_str}", styles["Footer"]))

    doc.build(elems)