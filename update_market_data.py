from __future__ import annotations

import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

HERE = Path(__file__).resolve().parent
OUT = HERE / "market_data.json"

UNIVERSE = [('AA', 'Alcoa', 'Basic Materials'), ('AAL', 'American Airlines', 'Industrials'), ('AAPL', 'Apple', 'Technology'), ('ABBV', 'ABBV', 'Healthcare'), ('ABNB', 'Airbnb', 'Consumer Cyclical'), ('ACHR', 'Archer Aviation', 'Industrials'), ('ADI', 'ADI', 'Technology'), ('ADM', 'ADM', 'Consumer Defensive'), ('ADSK', 'ADSK', 'Technology'), ('AEP', 'AEP', 'Utilities'), ('AES', 'AES', 'Utilities'), ('AFL', 'AFL', 'Financial Services'), ('AFRM', 'Affirm', 'Financial Services'), ('AI', 'C3.ai', 'Technology'), ('AJG', 'AJG', 'Financial Services'), ('AKAM', 'AKAM', 'Technology'), ('ALB', 'ALB', 'Basic Materials'), ('ALGN', 'ALGN', 'Healthcare'), ('ALL', 'ALL', 'Financial Services'), ('ALLY', 'Ally Financial', 'Financial Services'), ('AMAT', 'Applied Materials', 'Technology'), ('AMC', 'AMC Entertainment', 'Communication Services'), ('AMD', 'Advanced Micro Devices', 'Technology'), ('AMGN', 'AMGN', 'Healthcare'), ('AMT', 'AMT', 'Real Estate'), ('AMZN', 'Amazon', 'Consumer Cyclical'), ('ANET', 'ANET', 'Technology'), ('AON', 'AON', 'Financial Services'), ('APA', 'APA', 'Energy'), ('APD', 'APD', 'Basic Materials'), ('APO', 'APO', 'Financial Services'), ('APP', 'APP', 'Technology'), ('ARE', 'ARE', 'Real Estate'), ('ARM', 'ARM', 'Technology'), ('ASTS', 'AST SpaceMobile', 'Communication Services'), ('AVB', 'AVB', 'Real Estate'), ('AVGO', 'Broadcom', 'Technology'), ('AWK', 'AWK', 'Utilities'), ('AXP', 'AXP', 'Financial Services'), ('AZO', 'AZO', 'Consumer Cyclical'), ('BA', 'Boeing', 'Industrials'), ('BABA', 'BABA', 'Consumer Cyclical'), ('BAC', 'Bank of America', 'Financial Services'), ('BAX', 'Baxter', 'Healthcare'), ('BBAI', 'BigBear.ai', 'Technology'), ('BBY', 'Best Buy', 'Consumer Cyclical'), ('BG', 'BG', 'Consumer Defensive'), ('BIIB', 'BIIB', 'Healthcare'), ('BK', 'BK', 'Financial Services'), ('BKNG', 'Booking Holdings', 'Consumer Cyclical'), ('BKR', 'BKR', 'Energy'), ('BLK', 'BLK', 'Financial Services'), ('BMY', 'Bristol Myers Squibb', 'Healthcare'), ('BSX', 'BSX', 'Healthcare'), ('BX', 'BX', 'Financial Services'), ('BXP', 'BXP', 'Real Estate'), ('C', 'Citigroup', 'Financial Services'), ('CAH', 'CAH', 'Healthcare'), ('CARR', 'CARR', 'Industrials'), ('CAT', 'Caterpillar', 'Industrials'), ('CAVA', 'CAVA', 'Consumer Cyclical'), ('CB', 'CB', 'Financial Services'), ('CCI', 'CCI', 'Real Estate'), ('CCL', 'Carnival', 'Consumer Cyclical'), ('CDNS', 'CDNS', 'Technology'), ('CE', 'CE', 'Basic Materials'), ('CELH', 'CELH', 'Consumer Defensive'), ('CF', 'CF', 'Basic Materials'), ('CFG', 'CFG', 'Financial Services'), ('CHPT', 'ChargePoint', 'Industrials'), ('CHWY', 'Chewy', 'Consumer Cyclical'), ('CI', 'CI', 'Healthcare'), ('CL', 'CL', 'Consumer Defensive'), ('CLF', 'Cleveland-Cliffs', 'Basic Materials'), ('CMCSA', 'Comcast', 'Communication Services'), ('CME', 'CME', 'Financial Services'), ('CMG', 'CMG', 'Consumer Cyclical'), ('CMI', 'CMI', 'Industrials'), ('CNC', 'CNC', 'Healthcare'), ('COF', 'COF', 'Financial Services'), ('COIN', 'Coinbase', 'Financial Services'), ('COP', 'COP', 'Energy'), ('COR', 'COR', 'Healthcare'), ('COST', 'Costco', 'Consumer Defensive'), ('CPT', 'CPT', 'Real Estate'), ('CRM', 'Salesforce', 'Technology'), ('CRWD', 'CRWD', 'Technology'), ('CSCO', 'Cisco', 'Technology'), ('CSX', 'CSX', 'Industrials'), ('CTRA', 'CTRA', 'Energy'), ('CVS', 'CVS Health', 'Healthcare'), ('CVX', 'Chevron', 'Energy'), ('CZR', 'CZR', 'Consumer Cyclical'), ('D', 'D', 'Utilities'), ('DAL', 'Delta Air Lines', 'Industrials'), ('DASH', 'DASH', 'Consumer Cyclical'), ('DDOG', 'Datadog', 'Technology'), ('DE', 'Deere', 'Industrials'), ('DECK', 'DECK', 'Industrials'), ('DELL', 'Dell Technologies', 'Technology'), ('DHI', 'DHI', 'Consumer Cyclical'), ('DHR', 'DHR', 'Healthcare'), ('DIS', 'Walt Disney', 'Communication Services'), ('DKNG', 'DraftKings', 'Consumer Cyclical'), ('DLR', 'DLR', 'Real Estate'), ('DOCU', 'DOCU', 'Technology'), ('DOW', 'DOW', 'Basic Materials'), ('DPZ', 'DPZ', 'Consumer Cyclical'), ('DTE', 'DTE', 'Utilities'), ('DUK', 'Duke Energy', 'Utilities'), ('DUOL', 'DUOL', 'Technology'), ('DVN', 'DVN', 'Energy'), ('DXCM', 'DXCM', 'Healthcare'), ('EA', 'EA', 'Communication Services'), ('EBAY', 'EBAY', 'Consumer Cyclical'), ('ECL', 'ECL', 'Basic Materials'), ('ED', 'ED', 'Utilities'), ('EIX', 'EIX', 'Utilities'), ('ELV', 'ELV', 'Healthcare'), ('EMR', 'EMR', 'Industrials'), ('ENPH', 'ENPH', 'Technology'), ('EOG', 'EOG', 'Energy'), ('EQIX', 'EQIX', 'Real Estate'), ('EQR', 'EQR', 'Real Estate'), ('EQT', 'EQT', 'Energy'), ('ERIC', 'Ericsson', 'Technology'), ('ES', 'ES', 'Utilities'), ('ET', 'Energy Transfer', 'Energy'), ('ETN', 'ETN', 'Industrials'), ('ETSY', 'Etsy', 'Consumer Cyclical'), ('EW', 'EW', 'Healthcare'), ('EXC', 'EXC', 'Utilities'), ('EXPE', 'Expedia', 'Consumer Cyclical'), ('F', 'Ford', 'Consumer Cyclical'), ('FANG', 'FANG', 'Energy'), ('FAST', 'FAST', 'Industrials'), ('FCEL', 'FuelCell Energy', 'Energy'), ('FCX', 'FCX', 'Basic Materials'), ('FDX', 'FedEx', 'Industrials'), ('FE', 'FE', 'Utilities'), ('FI', 'FI', 'Financial Services'), ('FIS', 'FIS', 'Financial Services'), ('FITB', 'FITB', 'Financial Services'), ('FMC', 'FMC', 'Basic Materials'), ('FOX', 'FOX', 'Communication Services'), ('FOXA', 'FOXA', 'Communication Services'), ('FSLR', 'FSLR', 'Technology'), ('FTNT', 'FTNT', 'Technology'), ('FUBO', 'FuboTV', 'Communication Services'), ('GD', 'GD', 'Industrials'), ('GE', 'GE Aerospace', 'Industrials'), ('GEN', 'GEN', 'Technology'), ('GILD', 'Gilead Sciences', 'Healthcare'), ('GIS', 'GIS', 'Consumer Defensive'), ('GLW', 'GLW', 'Technology'), ('GM', 'General Motors', 'Consumer Cyclical'), ('GME', 'GameStop', 'Consumer Cyclical'), ('GOLD', 'Barrick Mining', 'Basic Materials'), ('GOOGL', 'Alphabet', 'Communication Services'), ('GPN', 'GPN', 'Financial Services'), ('GPRO', 'GoPro', 'Technology'), ('GRAB', 'Grab Holdings', 'Technology'), ('GS', 'Goldman Sachs', 'Financial Services'), ('GWW', 'GWW', 'Industrials'), ('HAL', 'Halliburton', 'Energy'), ('HBAN', 'HBAN', 'Financial Services'), ('HCA', 'HCA', 'Healthcare'), ('HD', 'HD', 'Consumer Cyclical'), ('HES', 'HES', 'Energy'), ('HIMS', 'Hims & Hers Health', 'Healthcare'), ('HOLX', 'HOLX', 'Healthcare'), ('HON', 'HON', 'Industrials'), ('HOOD', 'Robinhood', 'Financial Services'), ('HPQ', 'HP Inc.', 'Technology'), ('HSY', 'HSY', 'Consumer Defensive'), ('HUBS', 'HUBS', 'Technology'), ('HUM', 'HUM', 'Healthcare'), ('HWM', 'HWM', 'Industrials'), ('IAC', 'IAC', 'Communication Services'), ('IBM', 'IBM', 'Technology'), ('ICE', 'ICE', 'Financial Services'), ('IDXX', 'IDXX', 'Healthcare'), ('IFF', 'IFF', 'Basic Materials'), ('ILMN', 'ILMN', 'Healthcare'), ('INTC', 'Intel', 'Technology'), ('INVH', 'INVH', 'Real Estate'), ('IONQ', 'IonQ', 'Technology'), ('IPG', 'IPG', 'Communication Services'), ('IQV', 'IQV', 'Healthcare'), ('IR', 'IR', 'Industrials'), ('ISRG', 'ISRG', 'Healthcare'), ('ITW', 'ITW', 'Industrials'), ('JCI', 'JCI', 'Industrials'), ('JD', 'JD', 'Consumer Cyclical'), ('JNJ', 'Johnson & Johnson', 'Healthcare'), ('JNPR', 'JNPR', 'Technology'), ('JOBY', 'Joby Aviation', 'Industrials'), ('JPM', 'JPMorgan Chase', 'Financial Services'), ('KEY', 'KEY', 'Financial Services'), ('KEYS', 'KEYS', 'Technology'), ('KGC', 'Kinross Gold', 'Basic Materials'), ('KHC', 'KHC', 'Consumer Defensive'), ('KIM', 'KIM', 'Real Estate'), ('KKR', 'KKR', 'Financial Services'), ('KLAC', 'KLA', 'Technology'), ('KMB', 'KMB', 'Consumer Defensive'), ('KMI', 'Kinder Morgan', 'Energy'), ('KNTK', 'KNTK', 'Energy'), ('KO', 'Coca-Cola', 'Consumer Defensive'), ('KR', 'KR', 'Consumer Defensive'), ('KSS', "Kohl's", 'Consumer Cyclical'), ('LC', 'LendingClub', 'Financial Services'), ('LCID', 'Lucid Group', 'Consumer Cyclical'), ('LEN', 'LEN', 'Consumer Cyclical'), ('LI', 'Li Auto', 'Consumer Cyclical'), ('LIN', 'LIN', 'Basic Materials'), ('LLY', 'LLY', 'Healthcare'), ('LMT', 'Lockheed Martin', 'Industrials'), ('LOW', 'LOW', 'Consumer Cyclical'), ('LRCX', 'Lam Research', 'Technology'), ('LULU', 'LULU', 'Consumer Cyclical'), ('LUNR', 'Intuitive Machines', 'Industrials'), ('LUV', 'Southwest Airlines', 'Industrials'), ('LVS', 'LVS', 'Consumer Cyclical'), ('LYB', 'LYB', 'Basic Materials'), ('LYFT', 'Lyft', 'Consumer Cyclical'), ('M', "Macy's", 'Consumer Cyclical'), ('MA', 'MA', 'Financial Services'), ('MAA', 'MAA', 'Real Estate'), ('MAR', 'MAR', 'Consumer Cyclical'), ('MARA', 'MARA Holdings', 'Financial Services'), ('MCD', "McDonald's", 'Consumer Cyclical'), ('MCHP', 'MCHP', 'Technology'), ('MCK', 'MCK', 'Healthcare'), ('MCO', 'MCO', 'Financial Services'), ('MDB', 'MongoDB', 'Technology'), ('MDLZ', 'MDLZ', 'Consumer Defensive'), ('MDT', 'Medtronic', 'Healthcare'), ('MELI', 'MELI', 'Consumer Cyclical'), ('MET', 'MET', 'Financial Services'), ('META', 'Meta Platforms', 'Communication Services'), ('MGM', 'MGM', 'Consumer Cyclical'), ('MMC', 'MMC', 'Financial Services'), ('MMM', '3M', 'Industrials'), ('MNST', 'MNST', 'Consumer Defensive'), ('MO', 'MO', 'Consumer Defensive'), ('MOS', 'MOS', 'Basic Materials'), ('MPC', 'MPC', 'Energy'), ('MPWR', 'MPWR', 'Technology'), ('MRK', 'MRK', 'Healthcare'), ('MRNA', 'Moderna', 'Healthcare'), ('MRVL', 'Marvell Technology', 'Technology'), ('MS', 'Morgan Stanley', 'Financial Services'), ('MSFT', 'Microsoft', 'Technology'), ('MTB', 'MTB', 'Financial Services'), ('MTCH', 'MTCH', 'Communication Services'), ('MU', 'Micron Technology', 'Technology'), ('NCLH', 'Norwegian Cruise Line', 'Consumer Cyclical'), ('NEE', 'NextEra Energy', 'Utilities'), ('NEM', 'Newmont', 'Basic Materials'), ('NET', 'Cloudflare', 'Technology'), ('NFLX', 'Netflix', 'Communication Services'), ('NIO', 'NIO', 'Consumer Cyclical'), ('NKE', 'Nike', 'Consumer Cyclical'), ('NOC', 'NOC', 'Industrials'), ('NOK', 'Nokia', 'Technology'), ('NOW', 'ServiceNow', 'Technology'), ('NSC', 'NSC', 'Industrials'), ('NTAP', 'NTAP', 'Technology'), ('NTRS', 'NTRS', 'Financial Services'), ('NU', 'Nu Holdings', 'Financial Services'), ('NUE', 'NUE', 'Basic Materials'), ('NVDA', 'NVIDIA', 'Technology'), ('NWS', 'NWS', 'Communication Services'), ('NWSA', 'NWSA', 'Communication Services'), ('NXPI', 'NXPI', 'Technology'), ('O', 'Realty Income', 'Real Estate'), ('OKE', 'OKE', 'Energy'), ('OKTA', 'OKTA', 'Technology'), ('OMC', 'OMC', 'Communication Services'), ('ON', 'ON Semiconductor', 'Technology'), ('OPEN', 'Opendoor Technologies', 'Real Estate'), ('ORCL', 'Oracle', 'Technology'), ('ORLY', 'ORLY', 'Consumer Cyclical'), ('OXY', 'Occidental Petroleum', 'Energy'), ('PANW', 'PANW', 'Technology'), ('PARA', 'Paramount Skydance', 'Communication Services'), ('PATH', 'UiPath', 'Technology'), ('PBR', 'Petrobras', 'Energy'), ('PCAR', 'PCAR', 'Industrials'), ('PCG', 'PCG', 'Utilities'), ('PDD', 'PDD', 'Consumer Cyclical'), ('PEG', 'PEG', 'Utilities'), ('PEP', 'PepsiCo', 'Consumer Defensive'), ('PFE', 'Pfizer', 'Healthcare'), ('PG', 'PG', 'Consumer Defensive'), ('PH', 'PH', 'Industrials'), ('PHM', 'PHM', 'Consumer Cyclical'), ('PINS', 'Pinterest', 'Communication Services'), ('PLD', 'Prologis', 'Real Estate'), ('PLTR', 'Palantir', 'Technology'), ('PLUG', 'Plug Power', 'Energy'), ('PM', 'PM', 'Consumer Defensive'), ('PNC', 'PNC', 'Financial Services'), ('PPL', 'PPL', 'Utilities'), ('PRU', 'PRU', 'Financial Services'), ('PSA', 'PSA', 'Real Estate'), ('PSX', 'PSX', 'Energy'), ('PWR', 'PWR', 'Industrials'), ('PYPL', 'PayPal', 'Financial Services'), ('QBTS', 'D-Wave Quantum', 'Technology'), ('QCOM', 'Qualcomm', 'Technology'), ('QS', 'QuantumScape', 'Industrials'), ('RBLX', 'Roblox', 'Communication Services'), ('RCL', 'Royal Caribbean', 'Consumer Cyclical'), ('RDDT', 'RDDT', 'Technology'), ('REGN', 'REGN', 'Healthcare'), ('RF', 'RF', 'Financial Services'), ('RGTI', 'Rigetti Computing', 'Technology'), ('RIOT', 'Riot Platforms', 'Financial Services'), ('RIVN', 'Rivian', 'Consumer Cyclical'), ('RKLB', 'Rocket Lab USA', 'Industrials'), ('RMD', 'RMD', 'Healthcare'), ('ROK', 'ROK', 'Industrials'), ('ROST', 'ROST', 'Consumer Cyclical'), ('RTX', 'RTX', 'Industrials'), ('SAVA', 'Cassava Sciences', 'Healthcare'), ('SBUX', 'Starbucks', 'Consumer Cyclical'), ('SCHW', 'Charles Schwab', 'Financial Services'), ('SEDG', 'SEDG', 'Technology'), ('SHOP', 'Shopify', 'Technology'), ('SHW', 'SHW', 'Basic Materials'), ('SIRI', 'Sirius XM', 'Communication Services'), ('SLB', 'SLB', 'Energy'), ('SMCI', 'Super Micro Computer', 'Technology'), ('SNAP', 'Snap', 'Communication Services'), ('SNOW', 'Snowflake', 'Technology'), ('SNPS', 'SNPS', 'Technology'), ('SO', 'Southern Company', 'Utilities'), ('SOFI', 'SoFi Technologies', 'Financial Services'), ('SOUN', 'SoundHound AI', 'Technology'), ('SPG', 'Simon Property Group', 'Real Estate'), ('SPGI', 'SPGI', 'Financial Services'), ('SPOT', 'Spotify', 'Communication Services'), ('SRE', 'SRE', 'Utilities'), ('STE', 'STE', 'Healthcare'), ('STLD', 'STLD', 'Basic Materials'), ('STM', 'STMicroelectronics', 'Technology'), ('STT', 'STT', 'Financial Services'), ('STX', 'STX', 'Technology'), ('SYF', 'SYF', 'Financial Services'), ('SYK', 'SYK', 'Healthcare'), ('SYY', 'SYY', 'Consumer Defensive'), ('T', 'AT&T', 'Communication Services'), ('TDG', 'TDG', 'Industrials'), ('TDOC', 'Teladoc Health', 'Healthcare'), ('TEAM', 'TEAM', 'Technology'), ('TEL', 'TEL', 'Technology'), ('TFC', 'TFC', 'Financial Services'), ('TGT', 'Target', 'Consumer Defensive'), ('TJX', 'TJX', 'Consumer Cyclical'), ('TKO', 'TKO', 'Communication Services'), ('TMO', 'TMO', 'Healthcare'), ('TMUS', 'TMUS', 'Communication Services'), ('TOL', 'TOL', 'Consumer Cyclical'), ('TRGP', 'TRGP', 'Energy'), ('TRV', 'TRV', 'Financial Services'), ('TSLA', 'Tesla', 'Consumer Cyclical'), ('TT', 'TT', 'Industrials'), ('TTWO', 'TTWO', 'Communication Services'), ('TWLO', 'TWLO', 'Technology'), ('TXN', 'Texas Instruments', 'Technology'), ('U', 'U', 'Technology'), ('UAL', 'United Airlines', 'Industrials'), ('UBER', 'Uber', 'Consumer Cyclical'), ('UNH', 'UnitedHealth', 'Healthcare'), ('UNP', 'UNP', 'Industrials'), ('UPS', 'UPS', 'Industrials'), ('UPST', 'Upstart', 'Financial Services'), ('URI', 'URI', 'Industrials'), ('USB', 'USB', 'Financial Services'), ('V', 'V', 'Financial Services'), ('VALE', 'Vale', 'Basic Materials'), ('VICI', 'VICI Properties', 'Real Estate'), ('VLO', 'VLO', 'Energy'), ('VRSN', 'VRSN', 'Technology'), ('VRTX', 'VRTX', 'Healthcare'), ('VTR', 'VTR', 'Real Estate'), ('VTRS', 'Viatris', 'Healthcare'), ('VZ', 'Verizon', 'Communication Services'), ('W', 'Wayfair', 'Consumer Cyclical'), ('WAB', 'WAB', 'Industrials'), ('WBA', 'Walgreens Boots Alliance', 'Healthcare'), ('WBD', 'Warner Bros. Discovery', 'Communication Services'), ('WDAY', 'WDAY', 'Technology'), ('WDC', 'WDC', 'Technology'), ('WEC', 'WEC', 'Utilities'), ('WELL', 'WELL', 'Real Estate'), ('WFC', 'Wells Fargo', 'Financial Services'), ('WMB', 'WMB', 'Energy'), ('WMT', 'Walmart', 'Consumer Defensive'), ('WYNN', 'WYNN', 'Consumer Cyclical'), ('X', 'United States Steel', 'Basic Materials'), ('XEL', 'XEL', 'Utilities'), ('XOM', 'Exxon Mobil', 'Energy'), ('XPEV', 'XPeng', 'Consumer Cyclical'), ('XYZ', 'XYZ', 'Financial Services'), ('YUM', 'YUM', 'Consumer Cyclical'), ('ZBH', 'ZBH', 'Healthcare'), ('ZM', 'ZM', 'Technology'), ('ZS', 'ZS', 'Technology'), ('ZTS', 'ZTS', 'Healthcare')]
META = {ticker: {"name": name, "sector": sector} for ticker, name, sector in UNIVERSE}
TICKERS = [ticker for ticker, _, _ in UNIVERSE]

CHUNK_SIZE = 55
FEATURE_COLS = [
    "ret5", "ret20", "sma20_gap", "sma50_gap",
    "vol20", "volume_ratio", "rsi14"
]

def chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i+n]

def extract_series(frame: pd.DataFrame, field: str, ticker: str):
    if frame is None or frame.empty:
        return None
    if isinstance(frame.columns, pd.MultiIndex):
        l0 = set(map(str, frame.columns.get_level_values(0)))
        l1 = set(map(str, frame.columns.get_level_values(1)))
        try:
            if field in l0 and ticker in l1:
                return frame[(field, ticker)]
            if ticker in l0 and field in l1:
                return frame[(ticker, field)]
        except Exception:
            return None
        return None
    return frame[field] if field in frame.columns else None

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()
    x["ret1"] = x["Close"].pct_change(1)
    x["ret5"] = x["Close"].pct_change(5)
    x["ret20"] = x["Close"].pct_change(20)
    x["sma20"] = x["Close"].rolling(20).mean()
    x["sma50"] = x["Close"].rolling(50).mean()
    x["sma20_gap"] = x["Close"] / x["sma20"] - 1
    x["sma50_gap"] = x["Close"] / x["sma50"] - 1
    x["vol20"] = x["ret1"].rolling(20).std()
    vol_avg = x["Volume"].rolling(20).mean().replace(0, np.nan)
    x["volume_ratio"] = x["Volume"] / vol_avg
    x["rsi14"] = rsi(x["Close"])
    x["fwd5"] = x["Close"].shift(-5) / x["Close"] - 1
    return x.replace([np.inf, -np.inf], np.nan)

def historical_analog_prediction(df: pd.DataFrame) -> dict:
    """
    Five-trading-day outlook using historical analogs from the same stock.
    It compares today's momentum/trend/volatility/volume/RSI setup to prior setups,
    then summarizes what happened over the following five sessions.
    """
    x = feature_frame(df)
    current = x.iloc[-1]

    if any(pd.isna(current[c]) for c in FEATURE_COLS):
        return {
            "label": "Not enough data", "key": "neutral", "confidence": 0,
            "up_rate_pct": None, "expected_return_pct": None,
            "range_low_pct": None, "range_high_pct": None, "analogs": 0,
            "model": "Historical analog v1", "reasons": []
        }

    samples = x.iloc[:-5].dropna(subset=FEATURE_COLS + ["fwd5"]).copy()
    if len(samples) < 55:
        return {
            "label": "Not enough data", "key": "neutral", "confidence": 0,
            "up_rate_pct": None, "expected_return_pct": None,
            "range_low_pct": None, "range_high_pct": None, "analogs": int(len(samples)),
            "model": "Historical analog v1", "reasons": []
        }

    matrix = samples[FEATURE_COLS].astype(float)
    center = matrix.median()
    scale = matrix.std().replace(0, np.nan).fillna(1.0)
    cur = current[FEATURE_COLS].astype(float)

    z_samples = (matrix - center) / scale
    z_current = (cur - center) / scale

    # Give momentum/trend slightly more weight while retaining volatility/RSI context.
    weights = pd.Series(
        {"ret5": 1.2, "ret20": 1.25, "sma20_gap": 1.15, "sma50_gap": 1.0,
          "vol20": 0.8, "volume_ratio": 0.7, "rsi14": 0.65}
    )
    distances = (((z_samples - z_current) ** 2) * weights).sum(axis=1) ** 0.5

    k = min(28, max(14, int(math.sqrt(len(samples)) * 1.6)))
    nearest_idx = distances.nsmallest(k).index
    nearest = samples.loc[nearest_idx].copy()
    nearest_dist = distances.loc[nearest_idx].astype(float)

    # Nearby analogs carry more weight.
    analog_weights = 1.0 / (0.35 + nearest_dist)
    fwd = nearest["fwd5"].astype(float)

    weighted_mean = float(np.average(fwd, weights=analog_weights))
    weighted_up = float(np.average((fwd > 0).astype(float), weights=analog_weights))

    # Blend the historical analog result with a small current-trend component.
    trend_5d = float(current["ret20"]) / 4.0
    expected = 0.78 * weighted_mean + 0.22 * trend_5d
    trend_up = 1.0 / (1.0 + math.exp(-max(-4, min(4, trend_5d / 0.02))))
    up_rate = 0.82 * weighted_up + 0.18 * trend_up

    q20 = float(np.quantile(fwd, 0.20))
    q80 = float(np.quantile(fwd, 0.80))
    low = 0.82 * q20 + 0.18 * expected
    high = 0.82 * q80 + 0.18 * expected

    similarity = float(1.0 / (1.0 + nearest_dist.mean()))
    agreement = abs(up_rate - 0.5) * 2
    confidence = round(max(35, min(88, 42 + 27 * agreement + 22 * similarity)))

    if up_rate >= 0.66 and expected > 0:
        label, key = "Strong bullish", "bull"
    elif up_rate >= 0.56 and expected > -0.002:
        label, key = "Bullish", "bull"
    elif up_rate <= 0.34 and expected < 0:
        label, key = "Strong bearish", "bear"
    elif up_rate <= 0.44 and expected < 0.002:
        label, key = "Bearish", "bear"
    else:
        label, key = "Neutral", "neutral"

    reasons = []
    ret20 = float(current["ret20"])
    rsi14 = float(current["rsi14"])
    volume_ratio = float(current["volume_ratio"])
    sma20_gap = float(current["sma20_gap"])
    sma50_gap = float(current["sma50_gap"])

    if ret20 >= 0.08:
        reasons.append("strong 20-day momentum")
    elif ret20 <= -0.08:
        reasons.append("weak 20-day momentum")
    if sma20_gap > 0 and sma50_gap > 0:
        reasons.append("above 20- and 50-day averages")
    elif sma20_gap < 0 and sma50_gap < 0:
        reasons.append("below 20- and 50-day averages")
    if volume_ratio >= 1.4:
        reasons.append("above-average volume")
    if rsi14 >= 70:
        reasons.append("RSI elevated")
    elif rsi14 <= 30:
        reasons.append("RSI depressed")
    if not reasons:
        reasons.append("mixed technical setup")

    return {
        "label": label,
        "key": key,
        "confidence": confidence,
        "up_rate_pct": round(up_rate * 100, 1),
        "expected_return_pct": round(expected * 100, 2),
        "range_low_pct": round(low * 100, 2),
        "range_high_pct": round(high * 100, 2),
        "analogs": int(k),
        "model": "Historical analog v1",
        "reasons": reasons[:4],
    }

def build_record(ticker: str, close: pd.Series, volume: pd.Series | None):
    if close is None:
        return None

    df = pd.DataFrame({"Close": close})
    df["Volume"] = volume if volume is not None else 0
    df = df.dropna(subset=["Close"])
    if len(df) < 70:
        return None

    df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce").fillna(0)

    last = float(df["Close"].iloc[-1])
    prev = float(df["Close"].iloc[-2])
    if not math.isfinite(last) or last <= 0:
        return None

    change_pct = ((last - prev) / prev * 100.0) if prev else 0.0
    latest_volume = int(float(df["Volume"].iloc[-1]))
    avg_volume = int(float(df["Volume"].tail(20).mean()))

    sma20 = df["Close"].rolling(20).mean()
    sma50 = df["Close"].rolling(50).mean()

    history = []
    for idx, row in df.tail(260).iterrows():
        close_v = float(row["Close"])
        if not math.isfinite(close_v):
            continue
        i = df.index.get_loc(idx)
        s20 = sma20.iloc[i]
        s50 = sma50.iloc[i]
        history.append({
            "date": idx.strftime("%Y-%m-%d"),
            "close": round(close_v, 4),
            "volume": int(float(row["Volume"])),
            "sma20": None if pd.isna(s20) else round(float(s20), 4),
            "sma50": None if pd.isna(s50) else round(float(s50), 4),
        })

    meta = META.get(ticker, {"name": ticker, "sector": "Unknown"})
    prediction = historical_analog_prediction(df)

    return {
        "ticker": ticker,
        "name": meta["name"],
        "sector": meta["sector"],
        "price": round(last, 4),
        "previous_close": round(prev, 4),
        "change_pct": round(change_pct, 3),
        "volume": latest_volume,
        "avg_volume_20d": avg_volume,
        "market_cap": 0,
        "prediction": prediction,
        "history": history,
    }

def main():
    records = {}

    for group in chunks(TICKERS, CHUNK_SIZE):
        print(f"Downloading batch of {len(group)}...")
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
            print(f"Batch failed: {exc}")
            data = pd.DataFrame()

        for ticker in group:
            try:
                close = extract_series(data, "Close", ticker)
                volume = extract_series(data, "Volume", ticker)
                row = build_record(ticker, close, volume)
                if row:
                    records[ticker] = row
                    pred = row["prediction"]
                    print(f"OK {ticker} ${row['price']} | {pred['label']}")
                else:
                    print(f"SKIP {ticker}")
            except Exception as exc:
                print(f"SKIP {ticker}: {exc}")

        time.sleep(0.8)

    if not records:
        raise SystemExit("No stock data returned; refusing to overwrite market_data.json.")

    payload = {
        "updated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source": "yfinance prototype",
        "universe_size": len(TICKERS),
        "prediction_model": "Historical analog v1",
        "stocks": sorted(records.values(), key=lambda x: x["ticker"]),
    }

    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(records)} stocks out of {len(TICKERS)} requested.")

if __name__ == "__main__":
    main()
