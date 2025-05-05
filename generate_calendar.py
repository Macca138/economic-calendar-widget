import requests
from datetime import datetime, timedelta
import html

# Configuration
MAJOR_CURRENCIES = {"USD", "EUR", "GBP", "JPY", "AUD", "NZD", "CAD", "CHF"}
TODAY = datetime.utcnow().date()
TOMORROW = TODAY + timedelta(days=1)
URL = "https://cdn-nfs.faireconomy.media/ff_calendar_thisweek.json"

# Fetch and parse JSON
response = requests.get(URL)
response.raise_for_status()
data = response.json()

# Filter events
events = []
for item in data:
    event_date = datetime.strptime(item['date'], '%Y-%m-%d').date()
    if event_date not in [TODAY, TOMORROW]:
        continue
    if item['impact'] != 'High':
        continue
    if item['currency'] not in MAJOR_CURRENCIES:
        continue

    events.append({
        "date": event_date.strftime("%a %b %d"),
        "time": item['time'] + " UTC",
        "currency": item['currency'],
        "event": item['title'],
    })

# Generate HTML
html_output = """
<!DOCTYPE html>
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
"""

if not events:
    html_output += "<p>No high-impact events for today or tomorrow.</p>"
else:
    for e in events:
        html_output += f"""
  <div class="event">
    <div class="time">{html.escape(e['date'])} — {html.escape(e['time'])}</div>
    <div class="title">{html.escape(e['currency'])}: {html.escape(e['event'])}</div>
    <div class="impact">Impact: High</div>
  </div>
"""

html_output += "</body></html>"

# Write to index.html
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_output)
