from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yfinance as yf

HERE = Path(__file__).resolve().parent
OUT = HERE / "market_data.json"

# Starter universe: broad enough for useful filters, small enough for a free GitHub Actions prototype.
TICKERS = [
    "F","T","SOFI","NIO","RIVN","LCID","OPEN","PLUG","AAL","NU","GRAB","SNAP",
    "PFE","INTC","WBD","VALE","BAC","C","KGC","NOK","ERIC","SIRI","PARA","CSCO",
    "HPQ","PBR","UBER","LYFT","DKNG","HOOD","MARA","RIOT","HIMS","AFRM","RBLX",
    "PYPL","CMCSA","VZ","WBA","KSS"
]

def safe_info(ticker_obj):
    try:
        return ticker_obj.get_info() or {}
    except Exception:
        try:
            return ticker_obj.info or {}
        except Exception:
            return {}

def stock_record(ticker: str):
    obj = yf.Ticker(ticker)
    hist = obj.history(period="1y", interval="1d", auto_adjust=True)
    if hist is None or hist.empty:
        return None

    hist = hist.dropna(subset=["Close"])
    if len(hist) < 2:
        return None

    last = float(hist["Close"].iloc[-1])
    prev = float(hist["Close"].iloc[-2])
    change_pct = ((last - prev) / prev * 100.0) if prev else 0.0
    volume = int(hist["Volume"].iloc[-1]) if "Volume" in hist else 0
    avg_volume = int(hist["Volume"].tail(20).mean()) if "Volume" in hist and len(hist) else 0

    info = safe_info(obj)
    name = info.get("shortName") or info.get("longName") or ticker
    sector = info.get("sector") or info.get("industry") or "Unknown"
    market_cap = info.get("marketCap") or 0

    history = [
        {"date": idx.strftime("%Y-%m-%d"), "close": round(float(row["Close"]), 4)}
        for idx, row in hist.tail(260).iterrows()
    ]

    return {
        "ticker": ticker,
        "name": name,
        "sector": sector,
        "price": round(last, 4),
        "previous_close": round(prev, 4),
        "change_pct": round(change_pct, 3),
        "volume": volume,
        "avg_volume_20d": avg_volume,
        "market_cap": int(market_cap) if market_cap else 0,
        "history": history,
    }

def main():
    stocks = []
    for ticker in TICKERS:
        try:
            row = stock_record(ticker)
            if row:
                stocks.append(row)
                print(f"OK {ticker}: ${row['price']} | {row['sector']}")
            else:
                print(f"SKIP {ticker}: no data")
        except Exception as exc:
            print(f"SKIP {ticker}: {exc}")

    if not stocks:
        raise SystemExit("No stock data returned; refusing to overwrite market_data.json.")

    payload = {
        "updated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source": "yfinance prototype",
        "stocks": stocks,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(stocks)} stocks to {OUT}")

if __name__ == "__main__":
    main()
