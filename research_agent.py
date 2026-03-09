"""
Intelli-Credit — Research Agent v1.0
The "Digital Credit Manager" — Pillar 2 of Problem Statement

Covers:
- Auto web crawl for company + promoter news
- Sector headwinds (RBI regulations, industry trends)
- Legal/MCA filing search
- VADER sentiment analysis on all findings
- Risk score auto-adjustment based on research
"""

import requests
import urllib.parse
import time
from datetime import datetime, timedelta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# ── Sentiment Analyzer ────────────────────────────────────────────────────
analyzer = SentimentIntensityAnalyzer()

# ── Industry → Search Keywords Mapping ───────────────────────────────────
INDUSTRY_KEYWORDS = {
    "Textiles":        ["textile industry India", "cotton prices India", "garment export India"],
    "Pharmaceuticals": ["pharma India regulation", "USFDA India", "drug price control India"],
    "Manufacturing":   ["manufacturing India PMI", "industrial output India", "MSME India"],
    "Real Estate":     ["real estate India RBI", "housing market India", "RERA India"],
    "IT/Technology":   ["IT sector India", "tech layoffs India", "software exports India"],
    "NBFC/Finance":    ["RBI NBFC regulations", "NBFC liquidity India", "shadow banking India"],
    "Infrastructure":  ["infrastructure India budget", "road projects India", "HAM projects"],
    "Retail":          ["retail India GST", "FMCG India demand", "consumer spending India"],
    "Energy":          ["energy sector India", "renewable energy India", "power sector NPA"],
    "Other":           ["India corporate credit", "RBI monetary policy", "Indian economy outlook"],
}

# ── Google News RSS — No API Key Needed! ─────────────────────────────────
def fetch_google_news(query: str, max_results: int = 8) -> list:
    """
    Fetch news from Google News RSS feed.
    Free, no API key, works for any query.
    """
    try:
        encoded = urllib.parse.quote(query)
        url = f"https://news.google.com/rss/search?q={encoded}&hl=en-IN&gl=IN&ceid=IN:en"

        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=headers, timeout=8)

        if resp.status_code != 200:
            return []

        # Parse RSS XML manually (no lxml needed)
        import xml.etree.ElementTree as ET
        root = ET.fromstring(resp.content)
        channel = root.find("channel")
        if channel is None:
            return []

        items = []
        for item in channel.findall("item")[:max_results]:
            title   = item.findtext("title", "").strip()
            link    = item.findtext("link", "").strip()
            pubdate = item.findtext("pubDate", "").strip()
            source  = item.findtext("source", "").strip()

            if title:
                items.append({
                    "title":   title,
                    "link":    link,
                    "date":    pubdate[:16] if pubdate else "N/A",
                    "source":  source or "Google News",
                })
        return items

    except Exception as e:
        return []


# ── NewsAPI — Optional (if user has key) ─────────────────────────────────
def fetch_newsapi(query: str, api_key: str, max_results: int = 5) -> list:
    """
    Fetch from NewsAPI.org (free tier: 100 req/day)
    Get free key at: https://newsapi.org/register
    """
    try:
        from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query, "apiKey": api_key,
            "language": "en", "sortBy": "relevancy",
            "from": from_date, "pageSize": max_results,
        }
        resp = requests.get(url, params=params, timeout=8)
        data = resp.json()

        if data.get("status") != "ok":
            return []

        items = []
        for art in data.get("articles", []):
            items.append({
                "title":  art.get("title", ""),
                "link":   art.get("url", ""),
                "date":   (art.get("publishedAt") or "")[:10],
                "source": art.get("source", {}).get("name", "NewsAPI"),
            })
        return items

    except Exception:
        return []


# ── Sentiment Analysis ────────────────────────────────────────────────────
def analyze_sentiment(text: str) -> dict:
    """
    VADER sentiment on news title.
    Returns: score, label, emoji
    """
    scores = analyzer.polarity_scores(text)
    compound = scores["compound"]

    if compound >= 0.15:
        label, emoji, color = "Positive", "🟢", "positive"
    elif compound <= -0.15:
        label, emoji, color = "Negative", "🔴", "negative"
    else:
        label, emoji, color = "Neutral", "🟡", "neutral"

    return {
        "compound": round(compound, 3),
        "label": label,
        "emoji": emoji,
        "color": color,
        "positive": round(scores["pos"], 3),
        "negative": round(scores["neg"], 3),
        "neutral":  round(scores["neu"], 3),
    }


# ── Risk Keywords ─────────────────────────────────────────────────────────
HIGH_RISK_KEYWORDS = [
    "fraud", "scam", "default", "npa", "bankruptcy", "insolvency",
    "nclt", "ed raid", "cbi", "arrested", "money laundering", "cheating",
    "wilful defaulter", "sebi notice", "rbi penalty", "tax evasion",
    "promoter pledge", "insider trading", "price manipulation",
    "factory closed", "shutdown", "layoffs", "strike", "illegal",
    "court case", "lawsuit", "litigation", "fir", "chargesheet",
    "ponzi", "shell company", "circular trading",
]

MEDIUM_RISK_KEYWORDS = [
    "debt restructuring", "moratorium", "odr", "delay", "downgrade",
    "rating cut", "warning", "concern", "risk", "pressure", "stress",
    "slowdown", "decline", "loss", "negative outlook", "watch",
    "regulatory", "penalty", "fine", "violation", "non-compliance",
]

POSITIVE_KEYWORDS = [
    "profit", "growth", "expansion", "acquisition", "upgrade",
    "record revenue", "strong", "awarded", "contract", "export",
    "rating upgrade", "positive outlook", "dividend", "ipo",
    "tie-up", "partnership", "new order", "capacity expansion",
]


def classify_news_risk(title: str) -> str:
    """Classify a news headline as High/Medium/Low risk."""
    title_lower = title.lower()
    for kw in HIGH_RISK_KEYWORDS:
        if kw in title_lower:
            return "high"
    for kw in MEDIUM_RISK_KEYWORDS:
        if kw in title_lower:
            return "medium"
    for kw in POSITIVE_KEYWORDS:
        if kw in title_lower:
            return "positive"
    return "low"


# ══════════════════════════════════════════════════════════════════════════
# MAIN RESEARCH FUNCTION
# ══════════════════════════════════════════════════════════════════════════

def run_research_agent(
    company_name: str,
    industry: str,
    newsapi_key: str = "",
    max_news: int = 8,
) -> dict:
    """
    Full research pipeline for a company.

    Returns:
        research_score_adjustment: int (how much to ADD to risk score)
        findings: list of news items with sentiment
        sector_news: list of sector/regulatory news
        red_flags: list of critical negative findings
        summary: str (AI-generated summary)
        risk_label: str (Research Risk: Low/Medium/High)
    """

    findings        = []
    sector_news     = []
    red_flags       = []
    high_risk_count = 0
    med_risk_count  = 0
    positive_count  = 0

    # ── 1. Company-specific news ──────────────────────────────────────
    company_queries = [
        f"{company_name} India",
        f"{company_name} fraud OR default OR NPA OR legal",
        f"{company_name} promoter news",
    ]

    for query in company_queries:
        news = fetch_google_news(query, max_results=5)
        if not news and newsapi_key:
            news = fetch_newsapi(query, newsapi_key, max_results=5)

        for item in news:
            sentiment   = analyze_sentiment(item["title"])
            risk_level  = classify_news_risk(item["title"])

            finding = {
                **item,
                "query":      query,
                "sentiment":  sentiment,
                "risk_level": risk_level,
            }
            findings.append(finding)

            if risk_level == "high":
                high_risk_count += 1
                red_flags.append(f"🔴 {item['title'][:100]}")
            elif risk_level == "medium":
                med_risk_count += 1
            elif risk_level == "positive":
                positive_count += 1

        time.sleep(0.5)  # polite crawling

    # ── 2. Sector / Regulatory news ──────────────────────────────────
    sector_queries = INDUSTRY_KEYWORDS.get(industry, INDUSTRY_KEYWORDS["Other"])
    # Add generic Indian credit/RBI query
    sector_queries = sector_queries[:2] + ["RBI monetary policy India 2025"]

    for query in sector_queries:
        news = fetch_google_news(query, max_results=4)
        for item in news:
            sentiment  = analyze_sentiment(item["title"])
            risk_level = classify_news_risk(item["title"])
            sector_news.append({
                **item,
                "query":      query,
                "sentiment":  sentiment,
                "risk_level": risk_level,
            })
        time.sleep(0.5)

    # ── 3. Legal / MCA search ────────────────────────────────────────
    legal_query = f"{company_name} NCLT OR MCA OR court case OR legal dispute India"
    legal_news  = fetch_google_news(legal_query, max_results=5)
    for item in legal_news:
        sentiment  = analyze_sentiment(item["title"])
        risk_level = classify_news_risk(item["title"])
        finding = {
            **item,
            "query":      "Legal/MCA Search",
            "sentiment":  sentiment,
            "risk_level": risk_level,
        }
        findings.append(finding)
        if risk_level == "high":
            high_risk_count += 1
            red_flags.append(f"⚖️ {item['title'][:100]}")

    # ── 4. Calculate score adjustment ────────────────────────────────
    score_adj = 0
    score_adj += high_risk_count * 12   # each high risk news = +12 risk
    score_adj += med_risk_count  * 4    # each medium news = +4 risk
    score_adj -= positive_count  * 3    # each positive = -3 risk
    score_adj  = max(-15, min(40, score_adj))  # cap between -15 and +40

    # ── 5. Overall research risk label ───────────────────────────────
    if high_risk_count >= 2 or score_adj >= 20:
        research_risk = "High"
        risk_emoji    = "🔴"
    elif high_risk_count == 1 or score_adj >= 8:
        research_risk = "Medium"
        risk_emoji    = "🟡"
    else:
        research_risk = "Low"
        risk_emoji    = "🟢"

    # ── 6. Summary ───────────────────────────────────────────────────
    total_news = len(findings)
    neg_count  = sum(1 for f in findings if f["sentiment"]["label"] == "Negative")
    pos_count  = sum(1 for f in findings if f["sentiment"]["label"] == "Positive")

    if total_news == 0:
        summary = f"No significant news found for {company_name}. Clean web presence."
    else:
        summary_parts = [f"Found {total_news} news items for {company_name}."]
        if high_risk_count > 0:
            summary_parts.append(f"⚠️ {high_risk_count} HIGH RISK signals detected (fraud/legal/NPA keywords).")
        if neg_count > 0:
            summary_parts.append(f"{neg_count} negative sentiment articles found.")
        if pos_count > 0:
            summary_parts.append(f"{pos_count} positive articles found.")
        if score_adj > 10:
            summary_parts.append(f"Research findings increase risk score by +{score_adj} points.")
        elif score_adj < 0:
            summary_parts.append(f"Positive web presence reduces risk score by {score_adj} points.")
        summary = " ".join(summary_parts)

    return {
        "company_name":          company_name,
        "industry":              industry,
        "total_articles":        total_news,
        "high_risk_count":       high_risk_count,
        "medium_risk_count":     med_risk_count,
        "positive_count":        positive_count,
        "score_adjustment":      score_adj,
        "research_risk":         research_risk,
        "risk_emoji":            risk_emoji,
        "red_flags":             red_flags,
        "summary":               summary,
        "findings":              findings[:max_news],
        "sector_news":           sector_news[:8],
        "timestamp":             datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


# ── Quick test ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Testing Research Agent...")
    result = run_research_agent("Adani Enterprises", "Infrastructure")
    print(f"\nCompany: {result['company_name']}")
    print(f"Articles found: {result['total_articles']}")
    print(f"High risk: {result['high_risk_count']}")
    print(f"Score adjustment: +{result['score_adjustment']}")
    print(f"Research risk: {result['research_risk']}")
    print(f"\nSummary: {result['summary']}")
    print(f"\nRed Flags:")
    for f in result['red_flags']:
        print(f"  {f}")
    print(f"\nTop findings:")
    for f in result['findings'][:3]:
        print(f"  {f['sentiment']['emoji']} {f['title'][:80]}")