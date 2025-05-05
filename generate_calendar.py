import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import html
import random
import sys

# --- Configuration ---
TODAY = datetime.today().date()
TOMORROW = TODAY + timedelta(days=1)

MAJOR_COUNTRIES = [
    "united states", "euro zone", "united kingdom", "japan",
    "australia", "new zealand", "canada", "switzerland"
]

print(f"Looking for events from {TODAY} to {TOMORROW}")
print(f"Countries: {MAJOR_COUNTRIES}")

# User agent to avoid blocking
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15'
]

headers = {
    "User-Agent": random.choice(user_agents),
    "Accept-Language": "en-US,en;q=0.9",
}

# --- Function to get events for a specific date ---
def get_events_for_date(date):
    formatted_date = date.strftime("%Y-%m-%d")
    url = f"https://www.investing.com/economic-calendar/Service/getCalendarFilteredData"
    
    payload = {
        'country[]': '5,4,10,14,35,36,26,12,72',  # IDs for major countries
        'importance[]': '3',  # High importance only
        'timeZone': '8',  # GMT timezone
        'timeFilter': 'timeOnly',
        'dateFrom': formatted_date,
        'dateTo': formatted_date,
        'currentTab': 'custom',
        'limit_from': 0
    }
    
    headers_post = {
        "User-Agent": random.choice(user_agents),
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.investing.com/economic-calendar/"
    }
    
    try:
        response = requests.post(url, headers=headers_post, data=payload)
        response.raise_for_status()
        
        # The response is HTML content within JSON
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        events = []
        rows = soup.select('tr.js-event-item')
        
        for row in rows:
            try:
                # Get country
                country_element = row.select_one('td.flagCur span.ceFlags')
                if not country_element:
                    continue
                    
                country_code = country_element.get('title', '').lower()
                
                # Check if country is in major countries
                if not any(major_country in country_code.lower() for major_country in MAJOR_COUNTRIES):
                    continue
                
                # Get time
                time_element = row.select_one('td.time')
                if not time_element:
                    continue
                    
                event_time = time_element.text.strip()
                
                # Get event name
                event_element = row.select_one('td.event a')
                if not event_element:
                    continue
                    
                event_name = event_element.text.strip()
                
                # Store the event
                events.append({
                    "date": date.strftime("%a %b %d"),
                    "time": event_time,
                    "country": country_code.title(),
                    "event": event_name
                })
                
                print(f"Found event: {date.strftime('%Y-%m-%d')} - {event_time} - {country_code} - {event_name}")
                
            except Exception as e:
                print(f"Error parsing event: {e}")
                continue
                
        return events
        
    except Exception as e:
        print(f"Error fetching data for {formatted_date}: {e}")
        return []

# --- Get events for today and tomorrow ---
all_events = []

try:
    today_events = get_events_for_date(TODAY)
    all_events.extend(today_events)
    print(f"Found {len(today_events)} events for today")
    
    tomorrow_events = get_events_for_date(TOMORROW)
    all_events.extend(tomorrow_events)
    print(f"Found {len(tomorrow_events)} events for tomorrow")
    
except Exception as e:
    print(f"Error retrieving events: {e}")
    sys.exit(1)

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
    if not all_events:
        f.write("<p>No high-impact events for today or tomorrow.</p>")
        print("No events to display")
    else:
        for e in all_events:
            f.write(f"""
  <div class="event">
    <div class="time">{html.escape(e['date'])} — {html.escape(e['time'])} GMT</div>
    <div class="title">{html.escape(e['country'])}: {html.escape(e['event'])}</div>
    <div class="impact">Impact: High</div>
  </div>
""")
        print(f"Generated HTML with {len(all_events)} events")
    f.write("</body></html>")

print("Script completed successfully")