# Marcelo Stock Price Upgrade V4

This upgrade adds a second section to the existing Chromebook app:

- Low-price stock filters: under $5, $10, $20, or $50.
- Current share price.
- Daily percentage move.
- Sorting by lowest price, biggest daily gain, or ticker.
- A 30-trading-day line graph for each tracked stock.
- A separate GitHub Action that updates `market_data.json`.

## Files to upload/replace

Upload these into the ROOT of the existing GitHub repository:

- `index.html` — replace the old one.
- `manifest.json` — replace the old one.
- `update_market_data.py` — new.
- `market_data.json` — new starter file.

Create this workflow at:

`.github/workflows/update-market-data.yml`

using the included workflow file.

## After uploading

1. Commit everything to `main`.
2. Go to GitHub Actions.
3. Open **Update stock price feed**.
4. Click **Run workflow**.
5. Wait for the green check.
6. Wait for GitHub Pages to redeploy.
7. Reopen the Chromebook app or refresh it.
8. Click the new **Low-price stocks** tab.

## Change which stocks are tracked

Open `update_market_data.py` and edit the `TICKERS` list.

The initial list is only a starter watchlist. It is not a recommendation to buy those stocks.

## Data note

This prototype uses the third-party `yfinance` package and may show delayed data. For a commercial app, move to a licensed market-data provider.
