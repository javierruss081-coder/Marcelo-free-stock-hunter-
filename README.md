# Marcelo Free Stock Hunter — Chromebook V2.1

The older V2 relied on Python/Streamlit plus Windows/macOS launcher files. ChromeOS does not normally open those directly.

This version fixes that by making the front end a browser app.

## Quick test on Chromebook
1. Unzip the package in the Files app.
2. Open the `web` folder.
3. Open `index.html` in Chrome.
4. The app shows sample data immediately.

## Best setup: install it like an app
Host the `web` folder with GitHub Pages, open the Pages URL in Chrome, then use Chrome's **Install app** or **Create shortcut** option.

## Connect the live feed
In the app, open **Settings** and paste a public `offers.json` URL, for example:

`https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/web/offers.json`

The Chromebook interface itself needs no Python.

## Important
The app is only a promotion finder. Always verify eligibility, expiration, funding requirements, holding periods, withdrawal rules, taxes, and reward odds on the brokerage's official website.
