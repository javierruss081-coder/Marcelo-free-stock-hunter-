from __future__ import annotations

import json
from pathlib import Path

OFFERS = Path(__file__).resolve().parent / "offers.json"
OUT = Path(__file__).resolve().parent / "new_offer_alert.md"

if not OFFERS.exists():
    OUT.write_text("", encoding="utf-8")
    raise SystemExit(0)

data = json.loads(OFFERS.read_text(encoding="utf-8"))
new = [x for x in data if x.get("New")]

if not new:
    OUT.write_text("", encoding="utf-8")
    print("No new offers.")
    raise SystemExit(0)

lines = ["# New Stock Hunter offers", ""]
for o in new:
    lines += [
        f"## {o.get('Broker','Broker')} — {o.get('Offer','Offer')}",
        f"- Reward: {o.get('Reward','Verify terms')}",
        f"- Requirement: {o.get('Requirement','Verify terms')}",
        f"- Official source: {o.get('Source URL','')}",
        ""
    ]
OUT.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote alert for {len(new)} new offer(s).")
