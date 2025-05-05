import requests
import json
from datetime import datetime, timedelta
import html
import re
import sys

# --- Configuration ---
TODAY = datetime.today().date()
TOMORROW = TODAY + timedelta(days=1)

MAJOR_COUNTRIES = [
    "united states", "eurozone", "united kingdom", "japan",
    "australia", "new zealand", "canada", "switzerland"
]

# Convert to a list of country codes for the API
COUNTRY_CODES = {
    "united states": "US",
    "eurozone": "EU", 
    "united kingdom": "GB",
    "japan": "JP",
    "australia": "AU",
    "new zealand": "NZ",
    "canada": "CA",
    "switzerland": "CH"
}

print(f"Looking for events from {TODAY} to {TOMORROW}")
print(f"Countries: {MAJOR_COUNTRIES}")

# Use FXStreet's data feed, which is publicly accessible
def get_events(start_date, end_date):
    # Format dates for the API
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    # Base URL for the FXStreet economic calendar API
    url = f"https://calendar-api.fxstreet.com/en/api/v1/eventDates?culture=en-US&dateFrom={start_str}&dateTo={end_str}&famousEntitiesOnly=false&excludeCategories=Holiday"
    
    # Add user agent to mimic a browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json"
    }
    
    try:
        # Get dates first
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        dates_data = response.json()
        
        all_events = []
        
        # For each date returned, get the events
        for date_info in dates_data:
            date_str = date_info.get("date")
            
            events_url = f"https://calendar-api.fxstreet.com/en/api/v1/eventsByDate?culture=en-US&date={date_str}&famousEntitiesOnly=false&holidaysExcluded=true&view=normallist&volatilities=High"
            
            events_response = requests.get(events_url, headers=headers)
            events_response.raise_for_status()
            events_data = events_response.json()
            
            for event in events_data:
                # Check if event is from one of our major countries
                country = event.get("countryName", "").lower()
                if not any(major in country for major in MAJOR_COUNTRIES):
                    continue
                
                country_code = next((COUNTRY_CODES[major] for major in MAJOR_COUNTRIES if major in country), "")
                
                # Format the event datetime
                event_date = datetime.strptime(event.get("date", ""), "%Y-%m-%dT%H:%M:%SZ")
                
                # Skip holidays even if they somehow made it through
                event_name = event.get("name", "")
                if any(holiday in event_name.lower() for holiday in ["holiday", "bank holiday"]):
                    print(f"Skipping holiday: {event_name}")
                    continue
                
                all_events.append({
                    "id": event.get("id", ""),
                    "date": event_date.strftime("%a %b %d"),
                    "time": event_date.strftime("%H:%M"),
                    "country": country_code or country.title(),
                    "event": event_name
                })
                print(f"Found event: {event_date.strftime('%Y-%m-%d')} - {event_date.strftime('%H:%M')} - {country} - {event_name}")
        
        return all_events
        
    except Exception as e:
        print(f"Error retrieving events: {e}")
        return []

# --- Get events for today and tomorrow ---
try:
    all_events = get_events(TODAY, TOMORROW)
    print(f"Found {len(all_events)} events from {TODAY} to {TOMORROW}")
    
    # Remove duplicates by using a dictionary with event IDs as keys
    unique_events = {}
    for event in all_events:
        unique_events[event['id']] = event
    
    all_events = list(unique_events.values())
    print(f"After removing duplicates: {len(all_events)} events")
    
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