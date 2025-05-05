import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import html

TODAY = datetime.utcnow().date()
TOMORROW = TODAY + timedelta(days=1)
MAJOR_CURRENCIES = {"USD", "EUR", "GBP", "JPY", "AUD", "NZD", "CAD", "CHF"}

url = "https://www.forexfactory.com/calendar"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")
rows = soup.select("tr.calendar__row")
events = []

for row in rows:
    try:
        time_elem = row.select_one(".calendar__time")
        currency_elem = row.select_one(".calendar__currency")
        impact_elem = row.select_one(".impact--high")
        event_elem = row.select_one(".calendar__event-title")
        date_elem = row.find_previous("tr", class_="calendar__row--date")

        if not impact_elem:
            continue

        currency = currency_elem.text.strip() if currency_elem else ""
        if currency not in MAJOR_CURRENCIES:
            continue

        event_name = event_elem.text.strip() if event_elem else ""
        event_time = time_elem.text.strip() if time_elem else "All Day"

        if date_elem and date_elem.select_one(".calendar__date"):
            date_text = date_elem.select_one(".calendar__date").text.strip()
            try:
                event_date = datetime.strptime(date_text, "%a %b %d").replace(year=TODAY.year).date()
            except:
                event_date = TODAY
        else:
            event_date = TODAY

        if event_date in [TODAY, TOMORROW]:
            events.append({
                "date": event_date.strftime("%a %b %d"),
                "time": event_time + " UTC",
                "currency": currency,
                "event": event_name
            })
    except Exception:
        continue

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
    if not events:
        f.write("<p>No high-impact events for today or tomorrow.</p>\n")
    for e in events:
        f.write(f"""
  <div class="event">
    <div class="time">{html.escape(e['date'])} — {html.escape(e['time'])}</div>
    <div class="title">{html.escape(e['currency'])}: {html.escape(e['event'])}</div>
    <div class="impact">Impact: High</div>
  </div>
""")
    f.write("</body></html>")
