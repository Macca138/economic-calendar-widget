import requests
from ics import Calendar
from datetime import datetime, timedelta
import html

# --- CONFIGURATION ---
FEED_URL = "https://www.fxblue.com/Calendar/FxBlueCal.ics"
MAJOR_CURRENCIES = {"USD", "EUR", "GBP", "JPY", "AUD", "NZD", "CAD", "CHF"}
TODAY = datetime.utcnow().date()
TOMORROW = TODAY + timedelta(days=1)

# --- FETCH AND PARSE ICS FEED ---
response = requests.get(FEED_URL)
response.raise_for_status()
calendar = Calendar(response.text)

events = []
for event in calendar.events:
    event_start = event.begin.datetime.date()
    if event_start not in [TODAY, TOMORROW]:
        continue

    # Extract summary and description
    summary = event.name or ""
    description = event.description or ""

    # Must be high impact
    if "High" not in description:
        continue

    # Extract currency from summary
    currency = next((c for c in MAJOR_CURRENCIES if c in summary), None)
    if not currency:
        continue

    events.append({
        "date": event_start.strftime("%a %b %d"),
        "time": event.begin.format("HH:mm") + " UTC",
        "currency": currency,
        "event": summary.strip()
    })

# --- GENERATE HTML ---
with open("index.html", "w", encoding="utf-8") as f:
    f.write("""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>High-Impact Economic Events</title>
  <style>
    body { background: #1e1e1e; color: #fff; font-family: Arial; margin: 0; padding: 1rem; width: 250px; height: 500px; overflow-y: auto; }
    h3 { color: #f0ad4e; }
    .event { margin-bottom: 12px; border-bottom: 1px solid #444; padding-bottom: 6px; }
    .event .time { color: #999; font-size: 14px; }
    .event .title { font-weight: bold; font-size: 16px; }
    .event .impact { font-size: 12px; color: #f44336; }
  </style>
</head>
<body>
  <h3>High-Impact Economic Events</h3>
""")
    if not events:
        f.write("<p>No high-impact events for today or tomorrow.</p>")
    else:
        for e in events:
            f.write(f"""
  <div class="event">
    <div class="time">{html.escape(e['date'])} — {html.escape(e['time'])}</div>
    <div class="title">{html.escape(e['currency'])}: {html.escape(e['event'])}</div>
    <div class="impact">Impact: High</div>
  </div>
""")
    f.write("</body></html>")
