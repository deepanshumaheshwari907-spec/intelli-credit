# 🏦 Intelli-Credit: AI-Powered Corporate Credit Decision Engine

> **National AI/ML Hackathon — IIT Hyderabad × Vivriti Capital**
> Bridging the Intelligence Gap in Indian Corporate Lending

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://intellicredit.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![ML](https://img.shields.io/badge/ML-Random%20Forest%20%2B%20SHAP-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---
<img width="1916" height="914" alt="Screenshot 2026-03-09 140002" src="https://github.com/user-attachments/assets/65029c31-2225-4b13-8a8c-8c9728ba9bde" />
<img width="1640" height="899" alt="Screenshot 2026-03-09 140024" src="https://github.com/user-attachments/assets/07bbc18f-d44c-474d-9408-0050f34ebf5a" />
<img width="1516" height="841" alt="Screenshot 2026-03-09 140045" src="https://github.com/user-attachments/assets/96379960-a0ef-427f-b642-19b3b6d592dd" />
<img width="1605" height="855" alt="Screenshot 2026-03-09 140111" src="https://github.com/user-attachments/assets/e8fc255e-d835-412e-a6c2-8f1166c97934" />
<img width="1556" height="871" alt="Screenshot 2026-03-09 140128" src="https://github.com/user-attachments/assets/e04b4720-bb57-4659-9e44-38a645b28684" />
<img width="1612" height="855" alt="Screenshot 2026-03-09 140142" src="https://github.com/user-attachments/assets/ecd6529a-ba21-4483-9094-77131d706318" />
<img width="1546" height="846" alt="Screenshot 2026-03-09 140220" src="https://github.com/user-attachments/assets/5bd57e18-36d9-4576-bf1c-f91866804330" />
<img width="1613" height="853" alt="Screenshot 2026-03-09 140234" src="https://github.com/user-attachments/assets/5b1de54f-a33f-4f4e-82a5-66c25a9beaa9" />
<img width="1534" height="635" alt="Screenshot 2026-03-09 140241" src="https://github.com/user-attachments/assets/62012792-19c4-4f9a-a70b-96580279ee83" />

## 🎯 Problem Statement

In the Indian corporate lending landscape, credit managers face a **"Data Paradox"** — more information than ever, yet it takes **3–7 days** to process a single loan application.

Current manual process is:
- ⏱️ **Slow** — 200+ data points checked manually
- 🧠 **Biased** — inconsistent human judgment
- 📂 **Incomplete** — EWS signals buried in unstructured text
- 🚨 **Reactive** — NPAs detected too late

---

## ✅ Our Solution — Three Pillars

### 1. 📥 Data Ingestor
- PDF Annual Report upload & auto-parsing
- 12+ field structured financial form
- GST, CIBIL Commercial Score, MCA21 inputs
- Regex-based financial figure extraction

### 2. 🔍 Research Agent (Digital Credit Manager)
- Credit Officer primary notes portal
- NLP keyword sentiment analysis (VADER)
- Early Warning Signal detection (6 parameters)
- Negative news count & media sentiment scoring

### 3. 📊 Recommendation Engine
- Full Credit Appraisal Memo (CAM) PDF
- Specific loan amount + interest rate output
- 5 Cs weighted scorecard — fully explainable
- ML model (Random Forest + SHAP)

---

## 🚀 Features

| Feature | Description |
|---|---|
| **6-Ratio Analysis** | DSCR · ICR · D/E · EBITDA Margin · Current Ratio · Revenue Growth |
| **5 Cs Scorecard** | Capacity 35% · Capital 25% · Character 20% · Conditions 20% |
| **Indian Context** | GST compliance · CIBIL Score · MCA21 filing status |
| **ML + SHAP** | Random Forest · Probability distribution · SHAP waterfall chart |
| **Loan Recommendation** | Sanctioned amount · Interest rate · Tenure |
| **Early Warning Signals** | 6-parameter real-time EWS system |
| **Stress Testing** | 5 scenarios — Base · Stress · Severe · Recovery · Custom |
| **CAM PDF Report** | Bank-grade Credit Appraisal Memo download |
| **Portfolio Dashboard** | SQLite history · Pie chart · Exposure summary |
| **REST API** | FastAPI backend · Swagger UI · JSON responses |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   FRONTEND                          │
│              Streamlit UI (Dark Theme)              │
│         localhost:8501 / Streamlit Cloud            │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                   BACKEND                           │
│              FastAPI REST API                       │
│         localhost:8000 / Railway                    │
│                                                     │
│  POST /analyze  →  Full credit analysis             │
│  GET /portfolio →  Saved applications               │
│  GET /docs      →  Swagger UI                       │
└──────────────────────┬──────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼──────┐ ┌─────▼──────┐ ┌───▼──────────┐
│  Risk Engine │ │ ML Engine  │ │   Database   │
│  (Python)    │ │(RF + SHAP) │ │   (SQLite)   │
│              │ │            │ │              │
│ 5 Cs Model   │ │ 900 sample │ │ Borrower     │
│ 6 Ratios     │ │ trained    │ │ history      │
│ EWS System   │ │ 12 features│ │ Portfolio    │
└──────────────┘ └────────────┘ └──────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Python, Streamlit, Plotly |
| Backend | FastAPI, Uvicorn, Pydantic |
| ML/AI | Scikit-learn (Random Forest), SHAP, VADER NLP |
| Database | SQLite |
| PDF Parser | PyPDF2, ReportLab |
| Deployment | Streamlit Cloud, Railway |

---

## ⚡ Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/deepanshumaheshwari907-spec/intelli-credit.git
cd intelli-credit
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Streamlit App
```bash
streamlit run app.py
```

### 4. Run FastAPI Backend (new terminal)
```bash
uvicorn api:app --reload --port 8000
```

### 5. Open
```
Streamlit App  → http://localhost:8501
API Docs       → http://localhost:8000/docs
```

---

## 📡 API Usage

### Analyze a Company
```python
import requests

response = requests.post(
    "https://your-api-url.railway.app/analyze",
    json={
        "company_name":     "Sharma Steel Works Pvt Ltd",
        "industry":         "Manufacturing",
        "loan_amount":      20000000,
        "current_revenue":  85000000,
        "previous_revenue": 71000000,
        "ebitda":           12000000,
        "operating_income": 9500000,
        "interest_expense": 3200000,
        "total_debt":       32000000,
        "equity":           18000000,
        "current_assets":   22000000,
        "current_liabs":    16000000,
        "loan_obligation":  5500000,
        "promoter_stake":   62,
        "litigation_level": "Low",
        "negative_news":    1,
        "gst_compliance":   "Regular & Compliant",
        "cibil_score":      7.8,
        "mca_status":       "Up to Date"
    }
)

result = response.json()
print(f"Risk: {result['risk_category']}")
print(f"Score: {result['risk_score']}/100")
print(f"Loan: ₹{result['loan_rec']['sanctioned_amount']:,.0f}")
print(f"Rate: {result['loan_rec']['interest_rate']}% p.a.")
```

### Response
```json
{
  "risk_category": "Low Risk",
  "risk_score": 0,
  "decision": "Recommend Approval",
  "confidence": 92,
  "loan_rec": {
    "sanctioned_amount": 18000000,
    "interest_rate": 10.0,
    "tenure_years": 7
  },
  "ml_category": "Low Risk",
  "ml_confidence": 88.5
}
```

---

## 📁 Project Structure

```
intelli_credit/
│
├── app.py              # Streamlit frontend
├── api.py              # FastAPI backend
├── risk_engine.py      # Core risk scoring logic
├── ml_engine.py        # ML model + SHAP
├── database.py         # SQLite operations
├── cam_generator.py    # PDF report generator
├── requirements.txt    # Dependencies
└── README.md           # You are here!
```

---

## 🏆 Evaluation Criteria Coverage

| Criteria | How We Address It |
|---|---|
| **Extraction Accuracy** | PyPDF2 parser + regex extraction from Indian PDFs |
| **Research Depth** | NLP notes analysis + GST/CIBIL/MCA21 context |
| **Explainability** | SHAP waterfall charts + 5 Cs breakdown — zero black box |
| **Indian Context** | GST compliance · CIBIL Commercial · MCA21 · Industry benchmarks |

---

## 👥 Team

**Deepanshu Maheshwari** — Lead Developer & AI Engineer
Indore Institute of Science & Technology | AI/ML 2023

---

## 📄 License
MIT License — feel free to use and build upon this work.

---

<div align="center">
  <b>Intelli-Credit — Think like an analyst. Decide like a machine.</b>
</div>
