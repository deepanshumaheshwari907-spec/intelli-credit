"""
Intelli-Credit ML Engine
Random Forest model + SHAP explainability
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import shap
import warnings
warnings.filterwarnings("ignore")

# ── Feature names (must match order everywhere) ───────────────────────────
FEATURES = [
    "dscr", "debt_equity", "revenue_growth",
    "icr", "ebitda_margin", "current_ratio",
    "litigation_num", "negative_news", "promoter_stake",
    "industry_risk", "gst_num", "cibil_score"
]

FEATURE_LABELS = {
    "dscr":           "DSCR (Debt Service Coverage)",
    "debt_equity":    "Debt-to-Equity Ratio",
    "revenue_growth": "Revenue Growth %",
    "icr":            "Interest Coverage Ratio",
    "ebitda_margin":  "EBITDA Margin %",
    "current_ratio":  "Current Ratio",
    "litigation_num": "Litigation Level",
    "negative_news":  "Negative News Count",
    "promoter_stake": "Promoter Stake %",
    "industry_risk":  "Industry Risk Score",
    "gst_num":        "GST Compliance",
    "cibil_score":    "CIBIL Commercial Score",
}

# ── Encoders ──────────────────────────────────────────────────────────────
def _encode_litigation(level: str) -> float:
    return {"Low": 0.0, "Medium": 0.5, "High": 1.0}.get(level, 0.0)

def _encode_gst(status: str) -> float:
    return {
        "Regular & Compliant": 1.0,
        "Minor Delays":        0.6,
        "Frequent Defaults":   0.2,
        "Not Registered":      0.0,
    }.get(status, 0.6)

INDUSTRY_RISK_SCORE = {
    "IT / Technology": 0.10, "FMCG / Retail": 0.15,
    "Manufacturing": 0.20,   "Pharmaceuticals": 0.20,
    "Infrastructure": 0.30,  "Real Estate": 0.35,
    "Textiles": 0.30,        "Financial Services": 0.25,
    "Energy / Power": 0.25,  "Other": 0.20,
}

def build_feature_vector(data: dict) -> np.ndarray:
    return np.array([[
        min(data.get("dscr", 0), 5.0),
        min(data.get("debt_equity", 0), 6.0),
        max(min(data.get("revenue_growth", 0), 50), -50),
        min(data.get("icr", 0), 10.0),
        min(data.get("ebitda_margin", 0), 50),
        min(data.get("current_ratio", 0), 5.0),
        _encode_litigation(data.get("litigation_level", "Low")),
        min(data.get("negative_news", 0), 10),
        data.get("promoter_stake", 51) / 100,
        INDUSTRY_RISK_SCORE.get(data.get("industry", "Other"), 0.20),
        _encode_gst(data.get("gst_compliance", "Regular & Compliant")),
        data.get("cibil_score", 7.0) / 10.0,
    ]])


def _generate_synthetic_data(n: int = 800) -> tuple:
    """
    Generate synthetic but realistic corporate credit data.
    Labels: 0=Low Risk, 1=Medium Risk, 2=High Risk
    """
    rng = np.random.RandomState(42)

    rows, labels = [], []

    # Low risk profiles (~35%)
    for _ in range(int(n * 0.35)):
        rows.append([
            rng.uniform(1.5, 4.0),    # dscr
            rng.uniform(0.3, 1.8),    # d/e
            rng.uniform(5, 30),       # rev growth
            rng.uniform(2.5, 8.0),    # icr
            rng.uniform(15, 40),      # ebitda margin
            rng.uniform(1.33, 3.0),   # current ratio
            rng.choice([0.0, 0.0, 0.5]), # litigation
            rng.randint(0, 3),        # neg news
            rng.uniform(0.51, 0.85),  # promoter stake
            rng.uniform(0.10, 0.20),  # industry risk
            rng.choice([1.0, 1.0, 0.6]),  # gst
            rng.uniform(0.70, 1.0),   # cibil
        ])
        labels.append(0)

    # Medium risk profiles (~40%)
    for _ in range(int(n * 0.40)):
        rows.append([
            rng.uniform(1.1, 1.8),
            rng.uniform(1.5, 2.8),
            rng.uniform(-5, 15),
            rng.uniform(1.5, 3.0),
            rng.uniform(8, 18),
            rng.uniform(1.0, 1.5),
            rng.choice([0.0, 0.5, 0.5]),
            rng.randint(1, 5),
            rng.uniform(0.35, 0.60),
            rng.uniform(0.15, 0.30),
            rng.choice([1.0, 0.6, 0.6]),
            rng.uniform(0.50, 0.75),
        ])
        labels.append(1)

    # High risk profiles (~25%)
    for _ in range(int(n * 0.25)):
        rows.append([
            rng.uniform(0.3, 1.2),
            rng.uniform(2.5, 6.0),
            rng.uniform(-30, 5),
            rng.uniform(0.5, 1.8),
            rng.uniform(0, 10),
            rng.uniform(0.5, 1.2),
            rng.choice([0.5, 1.0, 1.0]),
            rng.randint(3, 10),
            rng.uniform(0.10, 0.40),
            rng.uniform(0.25, 0.35),
            rng.choice([0.2, 0.0, 0.6]),
            rng.uniform(0.20, 0.55),
        ])
        labels.append(2)

    X = np.array(rows)
    y = np.array(labels)
    idx = rng.permutation(len(y))
    return X[idx], y[idx]


# ── Train model once ──────────────────────────────────────────────────────
_X, _y = _generate_synthetic_data(900)

_scaler = StandardScaler()
_X_scaled = _scaler.fit_transform(_X)

_model = RandomForestClassifier(
    n_estimators=200, max_depth=8,
    min_samples_split=5, random_state=42, n_jobs=-1
)
_model.fit(_X_scaled, _y)

# SHAP explainer — RandomForest multi-class supported
_explainer = shap.TreeExplainer(_model)

RISK_LABELS = {0: "Low Risk", 1: "Medium Risk", 2: "High Risk"}


def ml_predict(data: dict) -> dict:
    """
    Run ML prediction on a single application.
    Returns label, probabilities, and SHAP values.
    """
    X = build_feature_vector(data)
    X_scaled = _scaler.transform(X)

    pred_class = int(_model.predict(X_scaled)[0])
    proba      = _model.predict_proba(X_scaled)[0]

    shap_vals  = _explainer.shap_values(X_scaled)   # shape: (n_classes, n_samples, n_features)
    sv_for_class = shap_vals[pred_class][0]          # (12,)

    # Build readable explanation
    feat_impact = sorted(
        zip(FEATURES, sv_for_class, X[0]),
        key=lambda x: abs(x[1]), reverse=True
    )

    top_risk     = [(FEATURE_LABELS[f], round(v, 3), round(r, 3))
                    for f, v, r in feat_impact if v > 0.01][:5]
    top_positive = [(FEATURE_LABELS[f], round(abs(v), 3), round(r, 3))
                    for f, v, r in feat_impact if v < -0.01][:4]

    return {
        "ml_category":   RISK_LABELS[pred_class],
        "ml_confidence": round(float(proba[pred_class]) * 100, 1),
        "probabilities": {
            "Low Risk":    round(float(proba[0]) * 100, 1),
            "Medium Risk": round(float(proba[1]) * 100, 1),
            "High Risk":   round(float(proba[2]) * 100, 1),
        },
        "shap_features": [f for f, v, r in feat_impact],
        "shap_values":   [round(v, 4) for f, v, r in feat_impact],
        "raw_values":    [round(r, 3) for f, v, r in feat_impact],
        "top_risk":      top_risk,
        "top_positive":  top_positive,
    }


def get_feature_importance() -> dict:
    """Global feature importance from the trained model."""
    imp = _model.feature_importances_
    return dict(sorted(
        zip([FEATURE_LABELS[f] for f in FEATURES], imp),
        key=lambda x: x[1], reverse=True
    ))