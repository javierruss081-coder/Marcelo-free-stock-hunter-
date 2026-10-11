from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import yfinance as yf

HERE = Path(__file__).resolve().parent
OUT = HERE / "market_data.json"

# Starter watchlist focused on liquid, commonly-followed lower-priced U.S. names.
# Edit this list whenever you want to track different tickers.
TICKERS = [
    "F", "T", "SOFI", "NIO", "RIVN", "LCID", "OPEN", "PLUG",
    "AAL", "NU", "GRAB", "SNAP", "PFE", "INTC", "WBD", "VALE"
]

def one_stock(ticker: str):
    t = yf.Ticker(ticker)
    hist = t.history(period="2mo", interval="1d", auto_adjust=True)
    if hist is None or hist.empty:
        return None

    hist = hist.dropna(subset=["Close"])
    if len(hist) < 2:
        return None

    recent = hist.tail(30)
    last = float(recent["Close"].iloc[-1])
    prev = float(recent["Close"].iloc[-2])
    change_pct = ((last - prev) / prev * 100.0) if prev else 0.0

    info = {}
    try:
        info = t.fast_info or {}
    except Exception:
        pass

    name = ticker
    try:
        full = t.info
        name = full.get("shortName") or full.get("longName") or ticker
    except Exception:
        pass

    history = [
        {"date": idx.strftime("%Y-%m-%d"), "close": round(float(row["Close"]), 4)}
        for idx, row in recent.iterrows()
    ]

    return {
        "ticker": ticker,
        "name": name,
        "price": round(last, 4),
        "change_pct": round(change_pct, 3),
        "history": history,
    }

def main():
    stocks = []
    for ticker in TICKERS:
        try:
            row = one_stock(ticker)
            if row:
                stocks.append(row)
                print(f"OK {ticker}: ${row['price']}")
            else:
                print(f"SKIP {ticker}: no data")
        except Exception as exc:
            print(f"SKIP {ticker}: {exc}")

    if not stocks:
        raise SystemExit("No market data was returned; refusing to overwrite market_data.json.")

    payload = {
        "updated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "stocks": stocks,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(stocks)} stocks to {OUT}")

if __name__ == "__main__":
    main()
