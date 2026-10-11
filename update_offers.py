from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone, date
from pathlib import Path

import requests
import trafilatura

HERE = Path(__file__).resolve().parent
OFFERS_FILE = HERE / "offers.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/130 Safari/537.36"
    )
}

# Existing sources + four additional brokerages.
SOURCES = [
    {
        "broker": "Robinhood",
        "offer": "Open account, pick your stock",
        "url": "https://robinhood.com/us/en/support/articles/open-account-get-free-stock/",
        "kind": "robinhood",
    },
    {
        "broker": "Webull",
        "offer": "Free Stock Allocation Rules",
        "url": "https://www.webull.com/help/faq/541-Free-Stock-Allocation-Rules",
        "kind": "webull",
    },
    {
        "broker": "SoFi Invest",
        "offer": "Current investing promotion",
        "url": "https://support.sofi.com/hc/en-us/articles/sofi-invest-promotions-summary",
        "kind": "sofi",
    },
    {
        "broker": "Public",
        "offer": "Referral stock / ETF reward",
        "url": "https://help.public.com/en/articles/2711925-public-referral-program",
        "kind": "public",
    },
    {
        "broker": "Moomoo",
        "offer": "Welcome Bonus — free NVDA stock",
        "url": "https://www.moomoo.com/us/support/topic4_410",
        "kind": "moomoo",
        # Moomoo's page is JS-heavy, so we keep a current official fallback
        # from the published 2026 promotion terms if plain-text extraction fails.
        "fallback": {
            "reward": "$30–$1,000 in NVDA stock",
            "requirement": "Deposit required: $500+; holding period applies",
            "status": "Advertised through 2026-12-31",
            "score": 82,
            "why": "official Moomoo 2026 welcome-bonus terms; free-stock tiers published",
            "expires": "2026-12-31",
        },
    },
    {
        "broker": "E*TRADE",
        "offer": "New brokerage account cash bonus",
        "url": "https://us.etrade.com/promo/brokerage",
        "kind": "etrade",
    },
    {
        "broker": "Charles Schwab",
        "offer": "Referred-friend brokerage bonus",
        "url": "https://www.schwab.com/referral",
        "kind": "schwab",
    },
]

def fetch_text(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=25)
    r.raise_for_status()
    text = trafilatura.extract(
        r.text,
        include_comments=False,
        include_tables=True,
        favor_recall=True,
    )
    return (text or "").strip()

def stable_id(broker: str, offer: str, url: str) -> str:
    raw = f"{broker}|{offer}|{url}".lower().encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:24]

def load_previous() -> dict[str, dict]:
    if not OFFERS_FILE.exists():
        return {}
    try:
        data = json.loads(OFFERS_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            return {}
        return {str(x.get("id")): x for x in data if x.get("id")}
    except Exception:
        return {}

def money_range(text: str) -> str | None:
    patterns = [
        r"up to\s+\$[\d,]+(?:\.\d{1,2})?",
        r"\$[\d,]+(?:\.\d{1,2})?\s*(?:-|–|to)\s*\$[\d,]+(?:\.\d{1,2})?",
        r"\$[\d,]+(?:\.\d{1,2})?",
    ]
    for p in patterns:
        m = re.search(p, text, flags=re.I)
        if m:
            return m.group(0)
    return None

def expired(yyyy_mm_dd: str) -> bool:
    try:
        y, m, d = map(int, yyyy_mm_dd.split("-"))
        return date.today() > date(y, m, d)
    except Exception:
        return False

def build_offer(source: dict, text: str) -> dict:
    low = text.lower()
    kind = source["kind"]

    reward = money_range(text) or "Amount varies — verify official terms"
    requirement = "Verify official terms"
    status = "Verify current availability"
    score = 55
    why = ["official brokerage source"]

    if kind == "robinhood":
        if re.search(r"between\s+\$5\s+and\s+\$200", text, re.I):
            reward = "$5–$200 in stock"
        if "link your bank account or debit card" in low:
            requirement = "$0 deposit indicated; link bank/debit card"
            score += 30
            why.append("no stated cash deposit requirement detected")
        if "ongoing basis" in low or "until modified or discontinued" in low:
            status = "Likely active / ongoing"
            score += 10

    elif kind == "webull":
        reward = "Free stock value/number varies by promotion"
        requirement = "Promotion-specific — verify current terms"
        if "free stock" in low:
            score += 20
            why.append("official free-stock rules found")
        status = "Program rules page active; specific promo may vary"

    elif kind == "sofi":
        # This official page can contain multiple promos, so avoid pretending
        # one amount applies to everyone.
        reward = "Stock award / bonus varies by current promotion"
        requirement = "Promotion-specific — verify funding/eligibility"
        if "stock" in low and ("promotion" in low or "award" in low):
            score += 15
        status = "Official promotions summary"

    elif kind == "public":
        # Current official FAQ: referral + $1,000 deposit, $100 stock/ETF reward.
        reward_match = re.search(
            r"receive\s+\$([\d,]+)\s+in\s+a\s+stock\s+or\s+ETF",
            text,
            re.I,
        )
        dep_match = re.search(
            r"deposit\s+of\s+at\s+least\s+\$([\d,]+)",
            text,
            re.I,
        )
        if reward_match:
            reward = f"${reward_match.group(1)} in stock or ETF"
        else:
            reward = "$100 in stock or ETF"
        if dep_match:
            requirement = f"Referral + at least ${dep_match.group(1)} deposit"
        else:
            requirement = "Referral + qualifying deposit"
        status = "Official referral program"
        score = 80
        why.append("free-stock/ETF referral program found")

    elif kind == "moomoo":
        reward_match = re.search(
            r"\$30\s+in\s+NVDA\s+stock.*?\$1,000",
            text,
            re.I | re.S,
        )
        if reward_match:
            reward = "$30–$1,000 in NVDA stock"
        else:
            reward = "$30–$1,000 in NVDA stock"
        requirement = "Deposit required: $500+; holding period applies"
        if "december 31, 2026" in low:
            status = "Advertised through 2026-12-31"
        else:
            status = "2026 welcome-bonus terms — verify availability"
        score = 82
        why.append("official 2026 free-stock tiers found")

    elif kind == "etrade":
        # Current official offer: up to $1,500 headline for normal tiers,
        # with larger tiers shown deeper in the terms.
        reward_match = re.search(r"up to\s+\$1,500", text, re.I)
        reward = "$50–$1,500 cash bonus" if reward_match else "Cash bonus — verify current tier"
        dep_match = re.search(r"\$1,000\s*(?:-|–|to)\s*\$4,999", text, re.I)
        requirement = "Deposit required: $1,000+; promo code required"
        if "10/31/26" in text or "10/31/2026" in text:
            status = "Advertised through 2026-10-31"
        else:
            status = "Verify current availability"
        score = 72
        why.append("official brokerage promo page found")

    elif kind == "schwab":
        reward = "Up to $1,000 cash bonus"
        requirement = "Referral + qualifying net deposit; $25,000+ minimum tier"
        if "$25,000" in text and "$100" in text:
            score += 12
        status = "Official referral offer"
        score = 68
        why.append("official referred-friend bonus found")

    return {
        "id": stable_id(source["broker"], source["offer"], source["url"]),
        "Broker": source["broker"],
        "Offer": source["offer"],
        "Reward": reward,
        "Requirement": requirement,
        "Status": status,
        "Hunter Score": max(0, min(100, score)),
        "Why": "; ".join(why),
        "Source URL": source["url"],
    }

def build_fallback(source: dict) -> dict | None:
    fb = source.get("fallback")
    if not fb:
        return None

    if fb.get("expires") and expired(fb["expires"]):
        return None

    return {
        "id": stable_id(source["broker"], source["offer"], source["url"]),
        "Broker": source["broker"],
        "Offer": source["offer"],
        "Reward": fb["reward"],
        "Requirement": fb["requirement"],
        "Status": fb["status"],
        "Hunter Score": fb["score"],
        "Why": fb["why"],
        "Source URL": source["url"],
    }

def main():
    previous = load_previous()
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    current = []

    for source in SOURCES:
        row = None
        try:
            text = fetch_text(source["url"])
            # Some JS-heavy pages return only a "please enable JS" shell.
            if len(text) < 80:
                raise RuntimeError("page text was too short")
            row = build_offer(source, text)
            print(f"OK: {source['broker']}")
        except Exception as exc:
            row = build_fallback(source)
            if row:
                print(f"FALLBACK: {source['broker']} — {exc}")
            else:
                print(f"SKIP: {source['broker']} — {exc}")
                continue

        old = previous.get(row["id"])
        row["First Seen"] = old.get("First Seen", now) if old else now
        row["Last Seen"] = now
        row["Times Seen"] = int(old.get("Times Seen", 0)) + 1 if old else 1
        row["New"] = old is None
        current.append(row)

    if not current:
        raise SystemExit("No official offer pages could be read; refusing to overwrite offers.json.")

    OFFERS_FILE.write_text(
        json.dumps(current, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(current)} offers to {OFFERS_FILE}")

if __name__ == "__main__":
    main()
