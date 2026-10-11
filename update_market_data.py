from __future__ import annotations

import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yfinance as yf

HERE = Path(__file__).resolve().parent
OUT = HERE / "market_data.json"

# V5.1 expanded universe.
# Tuple format: (ticker, company name, broad sector)
UNIVERSE = [
    # Technology
    ("AAPL","Apple","Technology"), ("MSFT","Microsoft","Technology"),
    ("NVDA","NVIDIA","Technology"), ("AMD","Advanced Micro Devices","Technology"),
    ("INTC","Intel","Technology"), ("CSCO","Cisco","Technology"),
    ("HPQ","HP Inc.","Technology"), ("DELL","Dell Technologies","Technology"),
    ("MU","Micron Technology","Technology"), ("QCOM","Qualcomm","Technology"),
    ("AVGO","Broadcom","Technology"), ("TXN","Texas Instruments","Technology"),
    ("AMAT","Applied Materials","Technology"), ("LRCX","Lam Research","Technology"),
    ("KLAC","KLA","Technology"), ("ON","ON Semiconductor","Technology"),
    ("MRVL","Marvell Technology","Technology"), ("STM","STMicroelectronics","Technology"),
    ("ERIC","Ericsson","Technology"), ("NOK","Nokia","Technology"),
    ("PLTR","Palantir","Technology"), ("SNOW","Snowflake","Technology"),
    ("CRM","Salesforce","Technology"), ("ORCL","Oracle","Technology"),
    ("IBM","IBM","Technology"), ("NOW","ServiceNow","Technology"),
    ("SHOP","Shopify","Technology"), ("NET","Cloudflare","Technology"),
    ("DDOG","Datadog","Technology"), ("MDB","MongoDB","Technology"),
    ("PATH","UiPath","Technology"), ("AI","C3.ai","Technology"),
    ("SOUN","SoundHound AI","Technology"), ("BBAI","BigBear.ai","Technology"),

    # Communication / media
    ("GOOGL","Alphabet","Communication Services"), ("META","Meta Platforms","Communication Services"),
    ("NFLX","Netflix","Communication Services"), ("DIS","Walt Disney","Communication Services"),
    ("CMCSA","Comcast","Communication Services"), ("T","AT&T","Communication Services"),
    ("VZ","Verizon","Communication Services"), ("WBD","Warner Bros. Discovery","Communication Services"),
    ("PARA","Paramount Skydance","Communication Services"), ("SNAP","Snap","Communication Services"),
    ("PINS","Pinterest","Communication Services"), ("RBLX","Roblox","Communication Services"),
    ("SPOT","Spotify","Communication Services"), ("SIRI","Sirius XM","Communication Services"),

    # Consumer / retail / travel
    ("AMZN","Amazon","Consumer Cyclical"), ("TSLA","Tesla","Consumer Cyclical"),
    ("F","Ford","Consumer Cyclical"), ("GM","General Motors","Consumer Cyclical"),
    ("RIVN","Rivian","Consumer Cyclical"), ("LCID","Lucid Group","Consumer Cyclical"),
    ("NIO","NIO","Consumer Cyclical"), ("XPEV","XPeng","Consumer Cyclical"),
    ("LI","Li Auto","Consumer Cyclical"), ("UBER","Uber","Consumer Cyclical"),
    ("LYFT","Lyft","Consumer Cyclical"), ("ABNB","Airbnb","Consumer Cyclical"),
    ("BKNG","Booking Holdings","Consumer Cyclical"), ("EXPE","Expedia","Consumer Cyclical"),
    ("AAL","American Airlines","Industrials"), ("DAL","Delta Air Lines","Industrials"),
    ("UAL","United Airlines","Industrials"), ("LUV","Southwest Airlines","Industrials"),
    ("CCL","Carnival","Consumer Cyclical"), ("NCLH","Norwegian Cruise Line","Consumer Cyclical"),
    ("RCL","Royal Caribbean","Consumer Cyclical"), ("DKNG","DraftKings","Consumer Cyclical"),
    ("CHWY","Chewy","Consumer Cyclical"), ("ETSY","Etsy","Consumer Cyclical"),
    ("W","Wayfair","Consumer Cyclical"), ("KSS","Kohl's","Consumer Cyclical"),
    ("M","Macy's","Consumer Cyclical"), ("BBY","Best Buy","Consumer Cyclical"),
    ("WMT","Walmart","Consumer Defensive"), ("TGT","Target","Consumer Defensive"),
    ("COST","Costco","Consumer Defensive"), ("KO","Coca-Cola","Consumer Defensive"),
    ("PEP","PepsiCo","Consumer Defensive"), ("SBUX","Starbucks","Consumer Cyclical"),
    ("MCD","McDonald's","Consumer Cyclical"), ("NKE","Nike","Consumer Cyclical"),

    # Financials / fintech
    ("JPM","JPMorgan Chase","Financial Services"), ("BAC","Bank of America","Financial Services"),
    ("C","Citigroup","Financial Services"), ("WFC","Wells Fargo","Financial Services"),
    ("GS","Goldman Sachs","Financial Services"), ("MS","Morgan Stanley","Financial Services"),
    ("SCHW","Charles Schwab","Financial Services"), ("HOOD","Robinhood","Financial Services"),
    ("SOFI","SoFi Technologies","Financial Services"), ("PYPL","PayPal","Financial Services"),
    ("AFRM","Affirm","Financial Services"), ("NU","Nu Holdings","Financial Services"),
    ("COIN","Coinbase","Financial Services"), ("MARA","MARA Holdings","Financial Services"),
    ("RIOT","Riot Platforms","Financial Services"), ("UPST","Upstart","Financial Services"),
    ("LC","LendingClub","Financial Services"), ("ALLY","Ally Financial","Financial Services"),

    # Healthcare
    ("PFE","Pfizer","Healthcare"), ("MRNA","Moderna","Healthcare"),
    ("BMY","Bristol Myers Squibb","Healthcare"), ("GILD","Gilead Sciences","Healthcare"),
    ("CVS","CVS Health","Healthcare"), ("WBA","Walgreens Boots Alliance","Healthcare"),
    ("HIMS","Hims & Hers Health","Healthcare"), ("TDOC","Teladoc Health","Healthcare"),
    ("SAVA","Cassava Sciences","Healthcare"), ("VTRS","Viatris","Healthcare"),
    ("BAX","Baxter","Healthcare"), ("MDT","Medtronic","Healthcare"),
    ("UNH","UnitedHealth","Healthcare"), ("JNJ","Johnson & Johnson","Healthcare"),

    # Energy / materials
    ("XOM","Exxon Mobil","Energy"), ("CVX","Chevron","Energy"),
    ("OXY","Occidental Petroleum","Energy"), ("HAL","Halliburton","Energy"),
    ("SLB","SLB","Energy"), ("PBR","Petrobras","Energy"),
    ("KMI","Kinder Morgan","Energy"), ("ET","Energy Transfer","Energy"),
    ("PLUG","Plug Power","Energy"), ("FCEL","FuelCell Energy","Energy"),
    ("VALE","Vale","Basic Materials"), ("KGC","Kinross Gold","Basic Materials"),
    ("GOLD","Barrick Mining","Basic Materials"), ("NEM","Newmont","Basic Materials"),
    ("CLF","Cleveland-Cliffs","Basic Materials"), ("AA","Alcoa","Basic Materials"),
    ("X","United States Steel","Basic Materials"),

    # Industrials / aerospace
    ("BA","Boeing","Industrials"), ("GE","GE Aerospace","Industrials"),
    ("CAT","Caterpillar","Industrials"), ("DE","Deere","Industrials"),
    ("MMM","3M","Industrials"), ("RTX","RTX","Industrials"),
    ("LMT","Lockheed Martin","Industrials"), ("UPS","UPS","Industrials"),
    ("FDX","FedEx","Industrials"), ("JOBY","Joby Aviation","Industrials"),
    ("ACHR","Archer Aviation","Industrials"), ("RKLB","Rocket Lab USA","Industrials"),

    # Real estate / utilities
    ("O","Realty Income","Real Estate"), ("VICI","VICI Properties","Real Estate"),
    ("PLD","Prologis","Real Estate"), ("SPG","Simon Property Group","Real Estate"),
    ("NEE","NextEra Energy","Utilities"), ("DUK","Duke Energy","Utilities"),
    ("SO","Southern Company","Utilities"), ("AES","AES","Utilities"),

    # Other liquid / popular
    ("GRAB","Grab Holdings","Technology"), ("OPEN","Opendoor Technologies","Real Estate"),
    ("GPRO","GoPro","Technology"), ("FUBO","FuboTV","Communication Services"),
    ("AMC","AMC Entertainment","Communication Services"), ("GME","GameStop","Consumer Cyclical"),
    ("CHPT","ChargePoint","Industrials"), ("QS","QuantumScape","Industrials"),
    ("IONQ","IonQ","Technology"), ("QBTS","D-Wave Quantum","Technology"),
    ("RGTI","Rigetti Computing","Technology"), ("ASTS","AST SpaceMobile","Communication Services"),
    ("LUNR","Intuitive Machines","Industrials"), ("SMCI","Super Micro Computer","Technology"),
]

META = {ticker: {"name": name, "sector": sector} for ticker, name, sector in UNIVERSE}
TICKERS = [ticker for ticker, _, _ in UNIVERSE]

CHUNK_SIZE = 40

def chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i+n]

def extract_series(frame: pd.DataFrame, field: str, ticker: str):
    """
    yfinance can return either:
    - columns MultiIndex: (Price, Ticker)
    - columns MultiIndex: (Ticker, Price)
    - normal columns for a single ticker
    """
    if frame is None or frame.empty:
        return None

    if isinstance(frame.columns, pd.MultiIndex):
        levels0 = set(map(str, frame.columns.get_level_values(0)))
        levels1 = set(map(str, frame.columns.get_level_values(1)))
        try:
            if field in levels0 and ticker in levels1:
                return frame[(field, ticker)]
            if ticker in levels0 and field in levels1:
                return frame[(ticker, field)]
        except Exception:
            return None
        return None

    if field in frame.columns:
        return frame[field]
    return None

def download_all():
    results = {}

    for group in chunks(TICKERS, CHUNK_SIZE):
        print(f"Downloading {len(group)} tickers...")
        try:
            data = yf.download(
                tickers=group,
                period="1y",
                interval="1d",
                auto_adjust=True,
                group_by="column",
                threads=True,
                progress=False,
            )
        except Exception as exc:
            print(f"Chunk failed: {exc}")
            data = pd.DataFrame()

        for ticker in group:
            close = extract_series(data, "Close", ticker)
            volume = extract_series(data, "Volume", ticker)
            if close is None:
                print(f"SKIP {ticker}: no close data")
                continue

            tmp = pd.DataFrame({"Close": close})
            if volume is not None:
                tmp["Volume"] = volume
            else:
                tmp["Volume"] = 0

            tmp = tmp.dropna(subset=["Close"])
            if len(tmp) < 2:
                print(f"SKIP {ticker}: insufficient history")
                continue

            last = float(tmp["Close"].iloc[-1])
            prev = float(tmp["Close"].iloc[-2])
            if not math.isfinite(last) or last <= 0:
                continue

            change_pct = ((last - prev) / prev * 100.0) if prev else 0.0
            vol = int(float(tmp["Volume"].iloc[-1])) if len(tmp) else 0
            avg_vol = int(float(tmp["Volume"].tail(20).mean())) if len(tmp) else 0

            history = [
                {"date": idx.strftime("%Y-%m-%d"), "close": round(float(row["Close"]), 4)}
                for idx, row in tmp.tail(260).iterrows()
                if math.isfinite(float(row["Close"]))
            ]

            meta = META.get(ticker, {"name": ticker, "sector": "Unknown"})
            results[ticker] = {
                "ticker": ticker,
                "name": meta["name"],
                "sector": meta["sector"],
                "price": round(last, 4),
                "previous_close": round(prev, 4),
                "change_pct": round(change_pct, 3),
                "volume": vol,
                "avg_volume_20d": avg_vol,
                # Keep 0 if a bulk market-cap source isn't available.
                # V5 handles missing caps as a neutral factor.
                "market_cap": 0,
                "history": history,
            }

        time.sleep(1)

    return list(results.values())

def main():
    stocks = download_all()
    if not stocks:
        raise SystemExit("No market data returned; refusing to overwrite market_data.json.")

    payload = {
        "updated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source": "yfinance prototype",
        "universe_size": len(TICKERS),
        "stocks": sorted(stocks, key=lambda x: x["ticker"]),
    }

    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(stocks)} stocks out of {len(TICKERS)} requested tickers.")

if __name__ == "__main__":
    main()
