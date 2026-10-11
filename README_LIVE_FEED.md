# Marcelo Live Feed Add-on

Add these files to the root GitHub repository that already contains:
`index.html`, `manifest.json`, `service-worker.js`, and `offers.json`.

Files:
- `update_offers.py`
- `.github/workflows/update-offers.yml`

The workflow can be run manually from GitHub Actions and also runs daily.

After the first successful run, connect the Chromebook app to:

https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/offers.json

For the current Marcelo repository shown in the setup screenshots:

https://raw.githubusercontent.com/javierruss081-coder/Marcelo-free-stock-hunter-/main/offers.json

The scanner reads only the listed official brokerage pages and writes the results to `offers.json`.
