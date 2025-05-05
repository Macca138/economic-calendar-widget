import investpy
from datetime import datetime, timedelta
import html

# --- Configuration ---
TODAY = datetime.today().date()
TOMORROW = TODAY + timedelta(days=1)
MAJOR_COUNTRIES = [
    "united states", "euro zone", "united kingdom", "japan",
    "australia", "new zealand", "canada", "switzerland"
]

# --- Fetch Economic Events ---
events = investpy.economic_calendar(
    time_zone='GMT', 
    countries=MAJOR_COUNTRIES,
    importances=['high']  # This filters for high importance events directly
)

# --- Filter Events ---
filtered_events = []
for _, event in events.iterrows():
    event_date = datetime.strptime(event['date'], "%d/%m/%Y").date()
    if event_date not in [TODAY, TOMORROW]:
        continue
    if event['importance'] != 'High':
        continue
    filtered_events.append({
        "date": event_date.strftime("%a %b %d"),
        "time": event['time'],
        "country": event['country'].title(),
        "event": event['event']
    })

# --- Generate HTML ---
with open("index.html", "w", encoding="utf-8") as f:
    f.write("""
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
""")
    if not filtered_events:
        f.write("<p>No high-impact events for today or tomorrow.</p>")
    else:
        for e in filtered_events:
            f.write(f"""
  <div class="event">
    <div class="time">{html.escape(e['date'])} — {html.escape(e['time'])} GMT</div>
    <div class="title">{html.escape(e['country'])}: {html.escape(e['event'])}</div>
    <div class="impact">Impact: High</div>
  </div>
""")
    f.write("</body></html>")
