"""
Intelli-Credit Database Module
SQLite-based persistent storage for borrower history & portfolio
"""

import sqlite3
import json
from datetime import datetime

DB_PATH = "intelli_credit.db"


def init_db():
    """Create tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at      TEXT    NOT NULL,
            company_name    TEXT    NOT NULL,
            industry        TEXT,
            loan_amount     REAL,
            risk_mode       TEXT,

            -- Financial Ratios
            dscr            REAL,
            debt_equity     REAL,
            revenue_growth  REAL,
            icr             REAL,
            ebitda_margin   REAL,
            current_ratio   REAL,

            -- Risk Results
            risk_score      INTEGER,
            risk_category   TEXT,
            decision        TEXT,
            confidence      INTEGER,

            -- Component scores
            capacity_risk   INTEGER,
            capital_risk    INTEGER,
            character_risk  INTEGER,
            conditions_risk INTEGER,

            -- Loan Recommendation
            sanctioned_amount REAL,
            interest_rate     REAL,
            tenure_years      INTEGER,

            -- Indian Context
            gst_compliance  TEXT,
            cibil_score     REAL,
            mca_status      TEXT,

            -- JSON blobs
            reasons         TEXT,
            positives       TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_application(data: dict) -> int:
    """Save a credit application. Returns the new row ID."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    lr = data.get("loan_rec", {})

    c.execute("""
        INSERT INTO applications (
            created_at, company_name, industry, loan_amount, risk_mode,
            dscr, debt_equity, revenue_growth, icr, ebitda_margin, current_ratio,
            risk_score, risk_category, decision, confidence,
            capacity_risk, capital_risk, character_risk, conditions_risk,
            sanctioned_amount, interest_rate, tenure_years,
            gst_compliance, cibil_score, mca_status,
            reasons, positives
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        data.get("company_name", "Unknown"),
        data.get("industry", ""),
        data.get("loan_amount", 0),
        data.get("risk_mode", "Balanced"),
        round(data.get("dscr", 0), 3),
        round(data.get("debt_equity", 0), 3),
        round(data.get("revenue_growth", 0), 3),
        round(data.get("icr", 0), 3),
        round(data.get("ebitda_margin", 0), 3),
        round(data.get("current_ratio", 0), 3),
        data.get("score", 0),
        data.get("category", ""),
        data.get("decision", ""),
        data.get("confidence", 0),
        data.get("capacity_risk", 0),
        data.get("capital_risk", 0),
        data.get("character_risk", 0),
        data.get("conditions_risk", 0),
        lr.get("sanctioned_amount", 0),
        lr.get("interest_rate", 0),
        lr.get("tenure_years", 0),
        data.get("gst_compliance", ""),
        data.get("cibil_score", 0),
        data.get("mca_status", ""),
        json.dumps(data.get("reasons", [])),
        json.dumps(data.get("positives", []))
    ))

    new_id = c.lastrowid
    conn.commit()
    conn.close()
    return new_id


def get_all_applications() -> list:
    """Return all applications as list of dicts."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM applications ORDER BY created_at DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()

    for r in rows:
        r["reasons"]   = json.loads(r["reasons"]   or "[]")
        r["positives"] = json.loads(r["positives"] or "[]")
    return rows


def get_portfolio_stats() -> dict:
    """Aggregate stats for portfolio dashboard."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM applications")
    total = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM applications WHERE risk_category='Low Risk'")
    low = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM applications WHERE risk_category='Medium Risk'")
    med = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM applications WHERE risk_category='High Risk'")
    high = c.fetchone()[0]

    c.execute("SELECT AVG(risk_score) FROM applications")
    avg_score = c.fetchone()[0] or 0

    c.execute("SELECT AVG(dscr) FROM applications WHERE dscr > 0")
    avg_dscr = c.fetchone()[0] or 0

    c.execute("SELECT SUM(loan_amount) FROM applications")
    total_exposure = c.fetchone()[0] or 0

    c.execute("SELECT SUM(sanctioned_amount) FROM applications WHERE risk_category != 'High Risk'")
    total_sanctioned = c.fetchone()[0] or 0

    conn.close()

    return {
        "total": total, "low": low, "medium": med, "high": high,
        "avg_score": round(avg_score, 1),
        "avg_dscr": round(avg_dscr, 2),
        "total_exposure": total_exposure,
        "total_sanctioned": total_sanctioned,
    }


def delete_application(app_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM applications WHERE id=?", (app_id,))
    conn.commit()
    conn.close()


# Auto-init on import
init_db()