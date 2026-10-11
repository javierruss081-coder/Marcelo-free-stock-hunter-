from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
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
        "offer": "3x Claw - Self-Directed Investing Promotion",
        "url": "https://support.sofi.com/hc/en-us/articles/3x-claw-self-directed-investing-promotion",
        "kind": "sofi_claw",
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

def first_money_range(text: str) -> str | None:
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

def build_offer(source: dict, text: str) -> dict:
    low = text.lower()
    broker = source["broker"]
    offer = source["offer"]
    url = source["url"]
    kind = source["kind"]

    reward = first_money_range(text) or "Amount varies — verify official terms"
    requirement = "Verify official terms"
    status = "Verify current availability"
    score = 55
    why = ["official brokerage source"]

    if kind == "robinhood":
        reward_match = re.search(r"between\s+\$5\s+and\s+\$200", text, flags=re.I)
        if reward_match:
            reward = "$5–$200"
        if "link your bank account or debit card" in low:
            requirement = "$0 deposit indicated; link bank/debit card"
            score += 30
            why.append("bank/debit link found without a stated cash deposit")
        if "ongoing basis" in low or "until modified or discontinued" in low:
            status = "Likely active / ongoing"
            score += 10
            why.append("ongoing-offer wording found")

    elif kind == "webull":
        reward = "Free stock value/number varies by promotion"
        requirement = "Promotion-specific — verify current terms"
        if "free stock program" in low:
            score += 15
            why.append("official free-stock program rules found")
        if "30 days to claim" in low:
            status = "Program rules page active; specific promo may vary"
            score += 5

    elif kind == "sofi_claw":
        range_match = re.search(
            r"stock ranging from\s+\$([\d,]+)\s*(?:-|–|to)\s*\$([\d,]+)",
            text,
            flags=re.I,
        )
        if range_match:
            reward = f"${range_match.group(1)}–${range_match.group(2)} in stock"
        deposit_match = re.search(
            r"(?:funded|funding requirement|minimum funding requirement)[^.\n]{0,100}?\$([\d,]+)",
            text,
            flags=re.I,
        )
        if deposit_match:
            requirement = f"Deposit required: at least ${deposit_match.group(1)}"
            score += 10
            why.append("minimum funding requirement found")
        period_match = re.search(
            r"(?:valid from|offer period:)[^.\n]{0,80}?(09/28/26|9/28/26)[^.\n]{0,80}?(10/18/26)",
            text,
            flags=re.I,
        )
        if period_match:
            status = "Advertised through 2026-10-18"
            score += 10
            why.append("current offer period found")

    score = max(0, min(100, score))

    return {
        "id": stable_id(broker, offer, url),
        "Broker": broker,
        "Offer": offer,
        "Reward": reward,
        "Requirement": requirement,
        "Status": status,
        "Hunter Score": score,
        "Why": "; ".join(why),
        "Source URL": url,
    }

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

def main():
    previous = load_previous()
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    current = []

    for source in SOURCES:
        try:
            text = fetch_text(source["url"])
            if not text:
                raise RuntimeError("page text was empty")
            row = build_offer(source, text)
            old = previous.get(row["id"])
            row["First Seen"] = old.get("First Seen", now) if old else now
            row["Last Seen"] = now
            row["Times Seen"] = int(old.get("Times Seen", 0)) + 1 if old else 1
            row["New"] = old is None
            current.append(row)
            print(f"OK: {row['Broker']} — {row['Offer']}")
        except Exception as exc:
            print(f"SKIP: {source['broker']} — {exc}")

    if not current:
        raise SystemExit("No official offer pages could be read; refusing to overwrite offers.json.")

    OFFERS_FILE.write_text(
        json.dumps(current, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(current)} offers to {OFFERS_FILE}")

if __name__ == "__main__":
    main()
